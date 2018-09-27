import uuid


class Meeting(object):
    def __init__(self, name, notes, time, current):
        self.name = name or uuid.uuid4().hex
        self.notes = notes
        self.time = time
        self.current = current

    def __repr__(self):
        return str(self.serialize())

    def serialize(self):
        return {'name': self.name, 'notes': self.notes, 'time': self.time, 'current': self.current}

    @staticmethod
    def deserialize(meeting_ndb_model):
        return Meeting(meeting_ndb_model.name, meeting_ndb_model.notes,
                       meeting_ndb_model.time, meeting_ndb_model.current)
