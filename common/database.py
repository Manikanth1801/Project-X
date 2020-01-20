import pymongo


class Database(object):
    @staticmethod
    def initialize():
        #client = pymongo.MongoClient("mongodb+srv://Test:Test123@cluster0-1n9p4.mongodb.net/test?retryWrites=true&w=majority")
        client = pymongo.MongoClient("mongodb://test:test123@ds359868.mlab.com:59868/heroku_pt0qk8kw")
        Database.DATABASE = client.get_default_database()

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)
