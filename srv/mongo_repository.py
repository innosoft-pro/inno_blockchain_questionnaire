from datetime import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient
# initialization of database
mongo_client = MongoClient('mongodb://mongo:27017')
mongo_db = mongo_client['polls']


class MongoRepository:
    """
    class for working with mongo_collections. Usage: create it in your class as a field with
    collection name in constructor and use its public methods.
    Attention: creates index by status field, possibly this need to be refactored because some collections might
    not have it
    """

    def __init__(self, collection_name):
        self._db = mongo_db
        self._collection = mongo_db[collection_name]

    def create_index(self, index_field, unique=False):
        """
        creates index on collection. 
        :param index_field: str, name of field to create index 
        :param unique: should index be unique or not
        :return: 
        """
        self._collection.create_index(index_field, unique=unique)

    def get_by_id(self, mongo_id):
        """
        :param mongo_id: str or ObjectId, id of document in mongo
        :return: dict - mongo document
        """
        result = self._collection.find_one({'_id': ObjectId(mongo_id)})
        return result

    def insert(self, item):
        """
        :param item: dict - mongo document
        :return: ObjectId - mongo id
        """
        insert_result = self._collection.insert_one(item)
        item['_id'] = str(insert_result.inserted_id)
        return item

    def update(self, item):
        """
        :param item: dict - existing mongo document (with valid '_id')
        :return: dict - updated item
        """
        result = self._collection.update_one(
            {'_id': item['_id']},
            {'$set': item}
        )
        if result.matched_count > 0:
            item['_id'] = str(item['_id'])
            return item
        else:
            raise RuntimeError('unsuccessful update attempt {}'.format(item['_id']))

    def get_cursor(self, pattern):
        """
        :param pattern: key field(s) for cursor (see pymongo docs for details)
        :return: pymongo cursor object
        """
        return self._collection.find(pattern)

    def find_one(self, pattern):
        """
        :param pattern: query filter (see pymongo docs for details)
        :return: mongo document or None if not exist
        """
        return self._collection.find_one(pattern)

    def delete_all(self):
        """
        removes all documents from collections
        :return
        """
        self._collection.remove({})
