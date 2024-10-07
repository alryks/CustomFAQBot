import pymongo
from bson import ObjectId

from typing import Optional

from config import DB


class ReportsDb:
    reports: pymongo.collection.Collection = DB.reports

    @classmethod
    def get_report(cls, report_id: ObjectId) -> Optional[dict]:
        return cls.reports.find_one({"_id": report_id})

    @classmethod
    def add_report(cls, data: dict) -> ObjectId:
        insert_result = cls.reports.insert_one(data)
        return insert_result.inserted_id

    @classmethod
    def edit_report(cls, report_id: ObjectId, data: dict) -> None:
        cls.reports.update_one({"_id": report_id}, {"$set": data})

    @classmethod
    def delete_report(cls, report_id: ObjectId) -> None:
        cls.reports.delete_one({"_id": report_id})


class UsersDb:
    users: pymongo.collection.Collection = DB.users

    @classmethod
    def get_users(cls) -> [dict]:
        return list(cls.users.find())

    @classmethod
    def get_user(cls, user_id: ObjectId) -> Optional[dict]:
        return cls.users.find_one({"_id": user_id})

    @classmethod
    def get_user_by_tg(cls, tg_id: int) -> Optional[dict]:
        return cls.users.find_one({"tg_id": tg_id})

    @classmethod
    def get_similar_users(cls, user_id: ObjectId) -> [dict]:
        user = cls.get_user(user_id)
        if user is None:
            return []
        query = {}
        for key, value in user.items():
            if isinstance(value, str) and value != "":
                query[key] = {"$regex": value, "$options": "i"}
        query["tg_id"] = {"$eq": 0}
        return list(cls.users.find(query))

    @classmethod
    def add_user(cls, data: dict) -> ObjectId:
        insert_result = cls.users.insert_one(data)
        return insert_result.inserted_id

    @classmethod
    def edit_user(cls, user_id: ObjectId, data: dict) -> None:
        cls.users.update_one({"_id": user_id}, {"$set": data})

    @classmethod
    def delete_user(cls, user_id: ObjectId) -> None:
        cls.users.delete_one({"_id": user_id})

    @classmethod
    def get_users_by_access(cls, access) -> [dict]:
        return list(cls.users.find({"access": access}))


class FaqDb:
    faq: pymongo.collection.Collection = DB.faq

    @classmethod
    def get_faq(cls) -> [dict]:
        return list(cls.faq.find())

    @classmethod
    def get_question(cls, question_id: ObjectId) -> Optional[dict]:
        return cls.faq.find_one({"_id": question_id})

    @classmethod
    def add_question(cls, question: str, answers: list[dict]) -> ObjectId:
        insert_result = cls.faq.insert_one({"question": question, "answers": answers})
        return insert_result.inserted_id

    @classmethod
    def edit_question(cls, question_id: ObjectId, question: str, answers: list[dict]) -> None:
        cls.faq.update_one({"_id": question_id}, {"$set": {"question": question, "answers": answers}})

    @classmethod
    def delete_question(cls, question_id: ObjectId) -> None:
        cls.faq.delete_one({"_id": question_id})
