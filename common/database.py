import pymongo
import datetime


class Database(object):
    @staticmethod
    def initialize():
        # client = pymongo.MongoClient("mongodb+srv://Test:Test123@cluster0-1n9p4.mongodb.net/test?retryWrites=true&w=majority")
        #client = pymongo.MongoClient("mongodb://test:test123@ds359868.mlab.com:59868/heroku_pt0qk8kw?retryWrites=false")
        client = pymongo.MongoClient("mongodb://test:test123@ds359868.mlab.com:59868/heroku_pt0qk8kw")
        Database.DATABASE = client.get_default_database()

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def update(collection, old_val, new_val):
        Database.DATABASE[collection].update({"username":old_val}, {"$set": {"username":new_val}})

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def update_confirm(collection, email):
        Database.DATABASE[collection].update({"email": email}, {"$set": {"confirmed": "True", "confirmed_on": datetime.datetime.now()}})
