import datetime
import uuid
from flask import session, flash, render_template
from passlib.hash import sha256_crypt

from common.database import Database
from models.blog import Blog


# added usertype
class User(object):
    def __init__(self, name, email, username, password, usertype, _id=None):
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.usertype = usertype
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email, username):
        # check either email or username exits in the database
        data1 = Database.find_one("test", {"email": email})
        if data1 is not None:
            return True
        else:
            data2 = Database.find_one("test", {"username": username})
            if data2 is not None:
                return True
        return False

    @staticmethod
    def login(email, password):
        # Check whether input is either username or password
        data1 = Database.find_one("test", {"username": email})
        data2 = Database.find_one("test", {"email": email})
        if (data1 or data2) is not None:
            if data1 is not None:
                dbPassword = data1['password']
            else:
                dbPassword = data2['password']
            if sha256_crypt.verify(password, dbPassword):
                session['logged_in'] = True
                if data1 is not None:
                    session['username'] = email
                else:
                    session['username'] = data2['username']
                flash('You are now logged in', 'success')
                return True
            else:
                flash('Invalid login')
                return render_template('login.html')
        else:
            flash('Username not found')
            return render_template('login.html')

    @classmethod
    def register(cls, name, email, username, password, usertype):
        user = cls.get_by_email(email, username)
        if user is False:
            # User doesn't exist, so we can create it
            enc_password = sha256_crypt.encrypt(str(password))
            new_user = cls(name, email, username, enc_password, usertype)
            new_user.save_to_mongo()
            session['username'] = username
            session['logged_in'] = True
            flash('You are now registered', 'success')
            return True
        else:
            return False

    @staticmethod
    def up_uname(nuname, puname, password):
        data1 = Database.find_one("test", {"username": puname})
        if data1 is not None:
            dbPassword = data1['password']
            if sha256_crypt.verify(password, dbPassword):
                dbPassword = data1['password']
                new_username = nuname
                old_username =puname
                Database.DATABASE["test"].update({"username": old_username}, {"$set":{"username": new_username}})
                session['username']=new_username
                flash("Hi {}, Your Username is Updated".format(new_username))
            else:
                flash("You might have entered wrong Username or Password")
        return True

    @staticmethod
    def logout():
        session.clear()
        flash('You are now logged out', 'success')
        return True

    def get_blogs(self):
        return Blog.find_by_author_id(self._id)

    def new_blog(self, title, description):
        blog = Blog(author=self.email,
                    title=title,
                    description=description,
                    author_id=self._id)

        blog.save_to_mongo()

    @staticmethod
    def new_post(blog_id, title, content, date=datetime.datetime.utcnow()):
        blog = Blog.from_mongo(blog_id)
        blog.new_post(title=title,
                      content=content,
                      date=date)

    def json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "type": self.usertype
        }

    def previous_uname(self):
        return {
            "username": self.username

        }

    def new_uname(self):
        return {
            "username": self.nuname
        }

    def save_to_mongo(self):
        Database.insert("test", self.json())

    def update_to_mongo(self):
        Database.update("test", self.previous_uname(), self.new_uname())


'''#add following fields in your db for organizer
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
        Database.insert("part", self.json_part())'''
