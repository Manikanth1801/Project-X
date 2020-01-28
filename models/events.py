import datetime
import uuid
from flask import session, flash, render_template
from passlib.hash import sha256_crypt

from common.database import Database
#from models.blog import Blog

class Event(object):
    def __init__(self, username, title, description, banner_image, address_line1, address_line2, city, state, country, terms_and_condition, event_category, event_date, event_time, contact_no, email, ticket_price, _id=None):
        self.username = username
        self.title = title
        self.description = description
        self.banner_image = banner_image
        self.address_line1 = address_line1
        self.address_line2 = address_line2
        self.city = city
        self.state = state
        self.country = country
        self.terms_and_condition = terms_and_condition
        self.event_category = event_category
        self.event_date = event_date
        self.event_time = event_time
        self.contact_no = contact_no
        self.email = email
        self.ticket_price = ticket_price        
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def create_event(cls, username, title, description, banner_image, address_line1, address_line2, city, state, country, terms_and_condition, event_category, event_date, event_time, contact_no, email, ticket_price):
    
        new_event = cls(username, title, description, banner_image, address_line1, address_line2, city, state, country, terms_and_condition, event_category, event_date, event_time, contact_no, email, ticket_price)
        new_event.save_event_mongo()
        flash('Event details has been added successfully', 'success')
        return True



def json_event(self):
        return {
            "_id": self._id,
            "username" = self.username
            "title" = self.title
            "description"= self.description
            "banner_image"= self.banner_image
            "address_line1"= self.address_line1
            "address_line2" = self.address_line2
            "city"= self.city
            "state"= self.state
            "country"= self.country
            "terms_and_condition"= self.terms_and_condition
            "event_category"= self.event_category
            "event_date"= self.event_date
            "event_time"= self.event_time
            "contact_no"= self.contact_no
            "email"= self.email
            "ticket_price"= self.ticket_price        
        }

    def save_event_mongo(self):
        Database.insert("event", self.json_event())
