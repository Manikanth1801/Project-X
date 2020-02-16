from models.events import Event
from models.user import User
from common.database import Database
import datetime
import uuid


class Booking(object):
    def __init__(self, event_id, user_id, _id=None):
        self.event_id = event_id
        self.user_id = user_id
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def new_booking(cls, event_id, user_id):
        booking = cls(event_id, user_id)
        booking.save_to_mongo()

    def save_to_mongo(self):
        Database.insert(collection='booking', data=self.json())

    def json(self):
        return {
            'booked_by': self.user_id,
            'event_id': self.event_id,
            'booked_on': datetime.datetime.utcnow(),
            '_id': self._id
        }
