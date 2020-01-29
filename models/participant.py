import datetime
import uuid
from flask import session, flash, render_template
from passlib.hash import sha256_crypt

from common.database import Database
from models.blog import Blog







#create participant collection and add following fields
class Participant(object):
    def __init__(self, preference1, preference2, preference3, part_username, state, city, _id=None):
        self.preference1 = preference1
        self.preference2 = preference2
        self.preference3 = preference3
        self.part_username = part_username
        self.state = state
        self.city = city
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def partRegister(cls, preference1, preference2, preference3, state, city):
        new_participant = cls(preference1, preference2, preference3, session['username'], state, city)
        new_participant.save_part_mongo()
        flash('Participant details has been added successfully', 'success')
        return True

    def json_part(self):
        return {
            "_id": self._id,
            "preference1": self.preference1,
            "preference2": self.preference2,
            "preference3": self.preference3,
            "username": session['username'],
            "state": self.state,
            "city": self.city
        }

    def save_part_mongo(self):
        Database.insert("part", self.json_part())
