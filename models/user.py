import datetime
import uuid
from flask import session, flash, render_template
from common.database import Database
from models.blog import Blog
from passlib.hash import sha256_crypt


class User(object):
    def __init__(self, name, email, username, password, _id=None):
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email, username):
        data1 = Database.find_one("users", {"email": email})
        data2 = Database.find_one("users", {"username": username})
        if data1 is not None:
            return cls(**data1)
        elif data2 is not None:
            return cls(**data2)
        return False

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login(email, password):
        # Check whether a user's email matches the password they sent us
        data1 = Database.find_one("users", {"username": email})
        data2 = Database.find_one("users", {"email": email})
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
    def register(cls, name, email, username, password):
        user = cls.get_by_email(email, username)
        if user is False:
            # User doesn't exist, so we can create it
            enc_password = sha256_crypt.encrypt(str(password))
            new_user = cls(name, email, username, enc_password)
            new_user.save_to_mongo()
            session['username'] = username
            session['logged_in'] = True
            flash('You are now registered', 'success')
            return True
        else:
            return False

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
            "password": self.password
        }

    def save_to_mongo(self):
        Database.insert("users", self.json())
