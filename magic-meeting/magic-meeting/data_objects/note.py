# from datetime import timedelta


class Note(object):
    def __init__(self, name, type, meeting_id, time, start_time_delta=None, assignee=None, description=None):
        self.name = name
        self.type = type
        self.meeting_id = meeting_id
        self.time = time
        self.start_time_delta = start_time_delta or "-30"
        self.assignee = assignee
        self.description = description

    def __repr__(self):
        return str(self.serialize())

    # def _get_audio_file_link(self):
    #     start_time = self.timestamp + timedelta(seconds=start_time_delta)

    def serialize(self):
        return {'name': self.name, 'type': self.type, 'meeting_id': self.meeting_id, 'time': self.name,
                'start_time_delta': self.type, 'assignee': self.assignee, 'description': self.description}

    @staticmethod
    def deserialize(note_ndb_model):
        return Note(note_ndb_model.name, note_ndb_model.type, note_ndb_model.meeting_id, note_ndb_model.time,
                    note_ndb_model.start_time_delta, note_ndb_model.assignee, note_ndb_model.description)
