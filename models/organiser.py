import datetime
import uuid
from flask import session, flash, render_template
from passlib.hash import sha256_crypt

from common.database import Database
from models.blog import Blog



#add following fields in your db for organizer
class Organizer(object):
    def __init__(self, org_name, org_email, org_username, address, _id=None):
        self.org_name = org_name
        self.org_email = org_email
        self.org_username = org_username
        self.address = address
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def orgRegister(cls, org_name, org_email, org_address):
        new_organiser = cls(org_name, org_email, session['username'], org_address)
        new_organiser.save_org_mongo()
        flash('Organizer details has been added successfully', 'success')
        return True

    def json_org(self):
        return {
            "_id": self._id,
            "org_name": self.org_name,
            "org_email": self.org_email,
            "username": session['username'],
            "address": self.address
        }

    def save_org_mongo(self):
        Database.insert("org", self.json_org())
