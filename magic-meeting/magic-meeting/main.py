#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json
import webapp2
import logging
from datetime import datetime
from ndb.queries import MeetingNdb, NoteNdb
from data_objects.meeting import Meeting
from data_objects.note import Note
import cloudstorage as gcs


class MagicMeetingHandler(webapp2.RequestHandler):
    meeting_ndb = MeetingNdb()
    note_ndb = NoteNdb()
    datetime_format = '%d/%m/%Y %H:%M:%S'
    default_bucket = 'meetings-audio'

    def allow_cors(self):
        self.response.headers.add_header('Access-Control-Allow-Origin', '*')
        self.response.headers.add_header('Access-Control-Allow-Headers', 'Authorization')
        self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE')

    def start_meeting(self):
        now = datetime.now()
        self.end_current_meeting()

        meeting_id = self.meeting_ndb.insert(
            Meeting(name=now.strftime(self.datetime_format), notes=[], time=now, current=True)
        )
        self.response.write('Successfully started meeting %s. (start time: %s)' % (meeting_id, now))

    def end_current_meeting(self):
        now = datetime.now()
        meeting_id = self._get_current_meeting_id()
        if not meeting_id:
            self.response.write('There is no current meeting at the moment.')
            return

        self.meeting_ndb.end_meeting(meeting_id)
        logging.info('Ended the meeting %s' % meeting_id)
        self.response.write('Successfully ended meeting %s. (end time: %s)' % (meeting_id, now))

    def get_meeting_summary(self, meeting_id):
        self.allow_cors()
        meeting = self.meeting_ndb.get(meeting_id)

        meeting_notes = list()
        for note_id in meeting.notes:
            note = self.note_ndb.get(note_id)
            secs = (note.time - meeting.time).total_seconds()
            meeting_notes.append({"id": note_id, "type": note.type, "time": secs})

        meeting_summary = {
            # "name": meeting.name,
            "url": "https://storage.googleapis.com/meetings-audio/%s.wav" % meeting_id,
            "notes": meeting_notes
        }
        self.response.write(json.dumps(meeting_summary))

    def get_current_meeting_summary(self):
        self.get_meeting_summary(self._get_current_meeting_id())

    def get_note_info(self, note_id):
        self.response.write(json.dumps(self.note_ndb.get(note_id).serialize()))

    def add_new_note(self):
        note_type = self.request.params.get('type')
        now = datetime.now()
        logging.debug('%s: note type: %s' % (now, note_type))

        meeting_id = self._get_current_meeting_id()
        if not meeting_id:
            self.response.status = 400
            self.response.write('There is no current meeting at the moment, cannot add note')
            return

        note = Note(name='', type=note_type, meeting_id=meeting_id, time=now)  # time=self._parse_note_time(note_time))
        note_id = self.note_ndb.insert(note)
        self.meeting_ndb.add_note(meeting_id, note_id)
        self.response.write('New note %s was added successfully to meeting %s.' % (note_id, meeting_id))

    def _get_current_meeting_id(self):
        return self.meeting_ndb.get_current_meeting()

    def save_meeting_audio(self):
        dest_filename = '%s.wav' % str(self._get_current_meeting_id())
        self.response.write('Uploading audio file to GCS as %s' % dest_filename)
        # self.end_current_meeting()
        self._upload_audio_to_gcs(self.request.body, dest_filename)

    def _upload_audio_to_gcs(self, file_content, dest_filename):
        self.response.write('Creating file %s in bucket %s' % (dest_filename, self.default_bucket))
        gcs_file = gcs.open("/" + self.default_bucket + "/" + dest_filename,
                            'w', content_type='audio/wav',
                            options={'x-goog-acl': 'public-read'},
                            retry_params=gcs.RetryParams(backoff_factor=1.1))
        gcs_file.write(file_content)
        gcs_file.close()

    def get(self):
        self.response.write('Hello world!')

    def options(self):
        self.allow_cors()


app = webapp2.WSGIApplication([
    webapp2.Route('/magic/meeting/start', MagicMeetingHandler, handler_method='start_meeting', methods=['GET']),
    # webapp2.Route('/magic/meeting/end', MagicMeetingHandler, handler_method='end_current_meeting', methods=['GET']),
    webapp2.Route('/magic/meeting/save', MagicMeetingHandler, handler_method='save_meeting_audio', methods=['POST']),
    webapp2.Route('/magic/meeting/summary', MagicMeetingHandler, handler_method='get_current_meeting_summary', methods=['GET']),
    # webapp2.Route('/magic/meeting/summary/<meeting_id>', MagicMeetingHandler, handler_method='get_meeting_summary', methods=['GET']),
    webapp2.Route('/magic/note/_add', MagicMeetingHandler, handler_method='add_new_note', methods=['POST']),
    webapp2.Route('/magic/note/<note_id>', MagicMeetingHandler, handler_method='get_note_info', methods=['GET']),
    ('/', MagicMeetingHandler)
], debug=True)


'''
def OLD_add_new_meeting(self):
    logging.debug('request body: %s' % self.request.body)
    logging.debug('request: %s' % self.request)
    meeting_summary = json.loads(self.request.body)
    logging.debug('meeting_summary: %s' % meeting_summary)
    meeting_name = meeting_summary.get('meeting_name')
    meeting_start_time = datetime.strptime(meeting_summary.get('meeting_start_time'), self.datetime_format)
    notes = meeting_summary.get('notes', '[]')

    meeting_id = self.meeting_ndb.insert(Meeting(meeting_name, [], meeting_start_time))
    note_ids = list()

    for note_data in notes:
        logging.debug('note_data: %s' % note_data)
        note = Note(
            name=note_data.get('name'),
            type=note_data.get('type'),
            meeting_id=meeting_id,
            time=datetime.strptime(note_data.get('time'), self.datetime_format),
            start_time_delta=note_data.get('start_time_delta'),
            assignee=note_data.get('assignee'),
            description=note_data.get('description')
        )
        note_id = self.note_ndb.insert(note)
        note_ids.append(int(note_id))

    self.meeting_ndb.update(meeting_id, meeting_notes=note_ids)
    self.response.write('Meeting %d was added successfully.' % meeting_id)
    
# TO TEST:
# cd C:\Users\Lynne\PycharmProjects\magic-meeting\meeting_summaries
# curl -v "http://magic-meeting.appspot.com/magic/_add" -H "Content-Type: application/json" -X POST --data-binary @meeting1.json
'''