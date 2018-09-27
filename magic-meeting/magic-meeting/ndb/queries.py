import logging

from models import Meeting as MeetingModel, Note as NoteModel
from data_objects.meeting import Meeting
from data_objects.note import Note


class MeetingNdb(object):
    def insert(self, meeting):
        logging.debug('inserting meeting: %s' % str(meeting))
        meeting_model = MeetingModel(name=meeting.name, time=meeting.time, notes=meeting.notes, current=meeting.current)
        meeting_key = meeting_model.put()
        logging.debug('successfully inserted meeting, id %d' % meeting_key.id())
        return meeting_key.id()

    def get(self, meeting_id):
        logging.debug('getting meeting %s' % meeting_id)
        meeting_model = MeetingModel.get_by_id(int(meeting_id))
        logging.debug('meeting model: %s' % meeting_model)
        if not meeting_model:
            logging.exception('no meeting with the given ID was found')
            raise Exception("meeting %s not found" % meeting_id)
        return Meeting.deserialize(meeting_model)

    def update(self, meeting_id, meeting_name=None, meeting_notes=None):
        meeting = MeetingModel.get_by_id(meeting_id)
        if meeting_name:
            meeting.name = meeting_name
        if meeting_notes:
            meeting.notes = meeting_notes
        meeting.put()

    def add_note(self, meeting_id, note_id):
        meeting = MeetingModel.get_by_id(meeting_id)
        meeting.notes = meeting.notes or list()
        meeting.notes.append(note_id)
        meeting.put()

    def end_meeting(self, meeting_id):
        meeting = MeetingModel.get_by_id(meeting_id)
        meeting.current = False
        meeting.put()

    def get_current_meeting(self):
        query = MeetingModel.query(MeetingModel.current==True)
        current_meetings = query.fetch()
        logging.debug('current_meetings: %s' % current_meetings)
        return current_meetings[-1].key.id() if current_meetings else None


class NoteNdb(object):
    def insert(self, note):
        logging.debug('inserting note: %s' % str(note))
        note_model = NoteModel(
            name=note.name, type=note.type, meeting_id=note.meeting_id, time=note.time,
            start_time_delta=note.start_time_delta, assignee=note.assignee, description=note.description
        )
        note_key = note_model.put()
        logging.debug('successfully inserted note, id %d' % note_key.id())
        return note_key.id()

    def get(self, note_id):
        note_model = NoteModel.get_by_id(int(note_id))
        if not note_model:
            raise Exception("note %s not found" % note_id)
        return Note.deserialize(note_model)

    def update(self, note_id, name=None, start_time_delta=None, assignee=None, description=None):
        note = NoteModel.get_by_id(note_id)
        if name:
            note.name = name
        if start_time_delta:
            note.start_time_delta = start_time_delta
        if assignee:
            note.assignee = assignee
        if description:
            note.description = description
        note.put()

