from datetime import datetime
from math import ceil
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
import os

dbhost = os.environ["MONGOHOST"]
dbname = os.environ["MONGODATABASE"]
dbuser = os.environ["MONGOUSER"]
dbpass = os.environ["MONGOPASSWORD"]
connection_string = f"mongodb://{dbuser}:{dbpass}@{dbhost}/{dbname}"


class DuplicateTitle(RuntimeError):
    pass


class CategoryQueries:
    def get_all_categories(self, page: int):
        client = MongoClient(connection_string)
        db = client[dbname]
        categories = list(
            db.categories.find()
                .sort("title", ASCENDING)
                .skip(page * 10)
                .limit(10)
        )
        for category in categories:
            clues_count = db.command({
                "count": "clues",
                "query": { "category_id": category["_id"] },
            })["n"]
            category["num_clues"] = clues_count
        page_count = ceil(db.command({"count": "categories"})["n"] / 100)
        return page_count, list(categories)

    def get_category(self, id: int):
        client = MongoClient(connection_string)
        db = client[dbname]
        category = db.categories.find_one({ "_id": id });
        return category

    def insert_category(self, title):
        client = MongoClient(connection_string)
        db = client[dbname]
        try:
            result = db.categories.insert_one({
                "title": title,
                "canon": False,
            });
            return self.get_category(result.inserted_id)
        except DuplicateKeyError:
            raise DuplicateTitle()

    def update_category(self, id, title):
        client = MongoClient(connection_string)
        db = client[dbname]
        try:
            result = db.categories.update_one(
                { "_id": id },
                { "$set": { "title": title } },
            )
            if result.matched_count == 0:
                return None
            return self.get_category(id)
        except DuplicateKeyError:
            raise DuplicateTitle()

    def delete_category(self, id):
        client = MongoClient(connection_string)
        db = client[dbname]
        db.clues.delete_many({ "category_id": id })
        db.categories.delete_one({ "_id": id })


class ClueQueries:
    def get_all_clues(self, page, value):
        client = MongoClient(connection_string)
        db = client[dbname]
        query_object = {}
        if value > 0:
            query_object["value"] = value
        clues = list(
            db.clues.find(query_object)
                .skip(page * 100)
                .limit(100)
        )
        for clue in clues:
            category = db.categories.find_one({ "_id": clue["category_id"] })
            clue["category"] = category
        page_count = ceil(db.command({"count": "clues"})["n"] / 100)
        return page_count, list(clues)

    def get_clue(self, id):
        client = MongoClient(connection_string)
        db = client[dbname]
        clue = db.clues.find_one({ "_id": id })
        category = db.categories.find_one({ "_id": clue["category_id"] })
        clue["category"] = category
        return clue

    def get_random_clue(self, count=1):
        client = MongoClient(connection_string)
        db = client[dbname]
        clues = list(db.clues.aggregate([
            { "$sample": { "size": count } },
        ]))
        for clue in clues:
            category = db.categories.find_one({ "_id": clue["category_id"] })
            clue["category"] = category
        if count == 1:
            return clues[0]
        return clues

    def increment_invalid_count(self, id):
        client = MongoClient(connection_string)
        db = client[dbname]
        db.clues.update_one(
            { "_id": id },
            { "$inc": { "invalid_count": 1 } },
        )
        clue = self.get_clue(id)
        category = db.categories.find_one({ "_id": clue["category_id"] })
        clue["category"] = category
        return clue


class GameQueries:
    def get_game(self, id):
        client = MongoClient(connection_string)
        db = client[dbname]
        result = db.games.aggregate([
            {"$match": { "_id": id }},
            {"$lookup": { "from": "clues", "localField": "_id", "foreignField": "game_id", "as": "clues" }},
            {"$project": {
                "total_amount_won": { "$sum": "$clues.value" },
                "episode_id": 1,
                "aired": 1,
                "canon": 1,
            }},
        ])
        result = list(result)
        return None if len(result) == 0 else result[0]


class CustomGameQueries:
    def create(self):
        clue_queries = ClueQueries()
        clues = clue_queries.get_random_clue(30)
        client = MongoClient(connection_string)
        db = client[dbname]
        result = db.custom_games.insert_one({
            "created_on": datetime.now(),
            "clues": clues,
        })
        return db.custom_games.find_one({ "_id": result.inserted_id })

    def get_custom_game(self, id):
        client = MongoClient(connection_string)
        db = client[dbname]
        return db.custom_games.find_one({ "_id": id })
