from google.appengine.ext import ndb


class Meeting(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    time = ndb.DateTimeProperty(indexed=True)
    notes = ndb.IntegerProperty(repeated=True)
    current = ndb.BooleanProperty(indexed=True)


class Note(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    type = ndb.StringProperty(indexed=True)
    meeting_id = ndb.IntegerProperty(indexed=True)
    time = ndb.DateTimeProperty(indexed=True)
    start_time_delta = ndb.StringProperty()
    assignee = ndb.StringProperty(indexed=True)
    description = ndb.StringProperty()

