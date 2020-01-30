import datetime
import uuid
from flask import session, flash, render_template
from passlib.hash import sha256_crypt

from common.database import Database
from models.blog import Blog



#add following fields in your db for organizer
class Organizer(object):
    def __init__(self, org_name, address1, address2, state, city, pin, org_phone, org_username, _id=None):
        self.org_name = org_name
        self.address1 = address1
        self.address2 = address2
        self.state = state
        self.city = city
        self.pin = pin
        self.org_phone = org_phone
        self.org_username = org_username
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def orgRegister(cls, org_name, address1, address2, state, city, pin, org_phone):
        new_organiser = cls(org_name, address1, address2, state, city, pin, org_phone, session['username'])
        new_organiser.save_org_mongo()
        flash('Organizer details has been added successfully', 'success')
        return True

    def json_org(self):
        return {
            "_id": self._id,
            "org_name": self.org_name,
            "address1": self.address1,
            "address2": self.address2,
            "state": self.state,
            "city": self.city,
            "pin": self.pin,
            "org_phone": self.org_phone,
            "username": session['username']
        }

    def save_org_mongo(self):
        Database.insert("org", self.json_org())
