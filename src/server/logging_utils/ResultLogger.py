import pymongo
from pymongo import MongoClient
from datetime import datetime
import json
from bson.objectid import ObjectId
import os
from ..config_utils import Config


class MongoDBConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MongoDBConnection, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.config = Config.get("mongo-dump-db")
        self.client = MongoClient(
            self.config["dump-db-mongo-uri"],
            username=self.config["dump-db-username"],
            password=self.config["dump-db-password"],
        )
        self.db = self.client[self.config["dump-db-name"]]
        self.collection = self.db[self.config["dump-db-collection"]]

    @classmethod
    def insert_json(
        cls, json_data, optional_id_string: str = None, time_to_parse: int = None
    ):
        instance = cls()
        document = {
            "unique_id": str(ObjectId()),
            "datetime": datetime.now(),
            "data": json_data,
            "optional_id_string": optional_id_string,
            "time_to_parse": time_to_parse,
        }
        instance.collection.insert_one(document)


class RecordLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RecordLogger, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.mongo_instance = MongoDBConnection()

    @classmethod
    def log_result(
        cls, json_data, optional_id_string: str = None, time_to_parse: int = None
    ):
        instance = cls()
        instance.mongo_instance.insert_json(
            json_data, optional_id_string, time_to_parse
        )
