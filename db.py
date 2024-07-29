import pymongo
from pymongo.errors import DuplicateKeyError

from bson import ObjectId

from telegram.ext import Application

from typing import Optional

from config import DB
from state import bots


class BotsDb:
    bots: pymongo.collection.Collection = DB.bots
    bots.create_index("bot_id", unique=True)

    @classmethod
    def get_bot(cls, bot_id: ObjectId) -> dict:
        return cls.bots.find_one({"_id": bot_id})

    @classmethod
    def get_bot_by_id(cls, bot_id: int) -> dict:
        return cls.bots.find_one({"bot_id": bot_id})

    @classmethod
    def get_bots(cls) -> [str]:
        return cls.bots.find({})

    @classmethod
    async def get_user_bot_usernames(cls, user_id: int) -> [(ObjectId, str)]:
        bot_ids = cls.bots.distinct("_id", {"admins": user_id})
        usernames = []
        for bot_id in bot_ids:
            if bot_id not in bots:
                continue
            app: Application = bots[bot_id].app
            if app is None:
                bots.pop(bot_id)
                continue
            try:
                usernames.append((bot_id, app.bot.bot.username))
            except:
                continue
        return usernames

    @classmethod
    def add_bot(cls, bot_id: int, bot_token: str, admin: int) -> Optional[
        ObjectId]:
        try:
            return cls.bots.insert_one({"bot_id": bot_id,
                                        "bot_token": bot_token,
                                        "admins": [admin],
                                        "is_private": False,
                                        "users": [],
                                        "caption": "",
                                        "faq": [],
                                        }).inserted_id
        except DuplicateKeyError:
            return None

    @classmethod
    def edit_token(cls, bot_id: ObjectId, bot_token: str) -> None:
        cls.bots.update_one({"_id": bot_id},
                            {"$set": {"bot_token": bot_token}})

    @classmethod
    def toggle_private(cls, bot_id: ObjectId) -> None:
        bot = cls.bots.find_one({"_id": bot_id})
        if bot is None:
            return
        cls.bots.update_one({"_id": bot_id},
                            {"$set": {"is_private": not bot["is_private"]}})

    @classmethod
    def is_admin(cls, bot_id: ObjectId, user_id: int) -> bool:
        bot = cls.bots.find_one({"_id": bot_id})
        if bot and user_id in bot.get("admins", []):
            return True
        return False

    @classmethod
    def add_admin(cls, bot_id: ObjectId, user_id: int) -> None:
        cls.bots.update_one({"_id": bot_id}, {"$addToSet": {"admins": user_id}})

    @classmethod
    def is_user(cls, bot_id: ObjectId, user_id: int) -> bool:
        bot = cls.bots.find_one({"_id": bot_id})
        user_ids = [user["tg_id"] for user in bot.get("users", [])]
        if bot and (not bot.get("is_private", False) or
                    user_id in user_ids or
                    user_id in bot.get("admins", [])):
            return True
        return False

    @classmethod
    def add_user_with_id(cls, bot_id: ObjectId, user_id: int) -> None:
        for user in cls.bots.find_one({"_id": bot_id}).get("users", []):
            if user.get("tg_id", 0) == user_id:
                print("User already exists")
                return
        cls.bots.update_one({"_id": bot_id}, {"$push": {"users": {
            "_id": ObjectId(),
            "tg_id": user_id,
        }}})

    @classmethod
    def add_user_with_data(cls, bot_id: ObjectId, name: str = "", job_title: str = "", unit: str = "", place: str = "", phone: str = "", email: str = "") -> ObjectId:
        user_id = ObjectId()
        cls.bots.update_one({"_id": bot_id}, {"$addToSet": {"users": {
            "_id": user_id,
            "tg_id": 0,
            "name": name,
            "job_title": job_title,
            "unit": unit,
            "place": place,
            "phone": phone,
            "email": email,
        }}})
        return user_id

    @classmethod
    def add_temp_user(cls, bot_id: ObjectId, user_id: int, name: str = "", job_title: str = "", unit: str = "", place: str = "", phone: str = "", email: str = "") -> ObjectId:
        user_oid = ObjectId()
        cls.bots.update_one({"_id": bot_id}, {"$addToSet": {"users": {
            "_id": user_oid,
            "tg_id": user_id,
            "name": name,
            "job_title": job_title,
            "unit": unit,
            "place": place,
            "phone": phone,
            "email": email,
            "is_temp": True,
        }}})
        return user_oid

    @classmethod
    def set_perm_user(cls, bot_id: ObjectId, user_id: ObjectId) -> None:
        cls.bots.update_one({"_id": bot_id, "users._id": user_id}, {"$unset": {"users.$.is_temp": ""}})

    @classmethod
    def delete_temp_user(cls, bot_id: ObjectId, user_id: ObjectId) -> None:
        bot_obj = cls.bots.find_one({"_id": bot_id, "users._id": user_id, "users.is_temp": True}, {"users.$": 1})
        if bot_obj is None:
            return
        users = bot_obj.get("users", [])
        if not users:
            return
        cls.bots.update_one({"_id": bot_id}, {"$pull": {"users": {"_id": user_id}}})

    @classmethod
    def edit_user(cls, bot_id: ObjectId, user_id: ObjectId, **kwargs) -> None:
        cls.bots.update_one({"_id": bot_id, "users._id": user_id}, {"$set": {f"users.$.{k}": v for k, v in kwargs.items() if v != ""}})

    @classmethod
    def reset_field(cls, bot_id: ObjectId, user_id: ObjectId, field: str) -> None:
        cls.bots.update_one({"_id": bot_id, "users._id": user_id}, {"$set": {f"users.$.{field}": ""}})

    @classmethod
    def get_users_to_merge(cls, bot_id: ObjectId) -> [dict]:
        bot = cls.bots.find_one({"_id": bot_id})
        users = bot.get("users", [])
        users = [user for user in users if user.get("tg_id", 0) != 0]
        return users

    @classmethod
    def merge_id_and_data_users(cls, bot_id: ObjectId, id_user: ObjectId, data_user: ObjectId) -> bool:
        users = cls.bots.find_one({"_id": bot_id, "users._id": id_user}, {"users.$": 1}).get("users", [])
        if not users:
            return False
        id_user_obj = users[0]
        cls.bots.update_one({"_id": bot_id, "users._id": data_user}, {"$set": {"users.$.tg_id": id_user_obj["tg_id"]}})
        cls.bots.update_one({"_id": bot_id}, {"$pull": {"users": {"_id": id_user}}})
        return True

    @classmethod
    def unmerge_user(cls, bot_id: ObjectId, user_id: ObjectId) -> bool:
        users = cls.bots.find_one({"_id": bot_id, "users._id": user_id}, {"users.$": 1}).get("users", [])
        if not users:
            return False
        user = users[0]
        if user.get("name", "") == "":
            return False

        cls.bots.update_one({"_id": bot_id, "users._id": user_id}, {"$set": {"users.$.tg_id": 0}})
        cls.add_user_with_id(bot_id, user["tg_id"])
        return True

    @classmethod
    def get_user(cls, bot_id: ObjectId, user_id: ObjectId) -> Optional[dict]:
        bot_obj = cls.bots.find_one({"_id": bot_id, "users._id": user_id}, {"users.$": 1})
        if bot_obj is None:
            return
        if bot_obj["users"]:
            return bot_obj["users"][0]

    @classmethod
    def toggle_required(cls, bot_id: ObjectId, field: str) -> None:
        bot = cls.bots.find_one({"_id": bot_id})
        if bot is None:
            return
        if "required_fields" not in bot:
            return
        cls.bots.update_one({"_id": bot_id}, {"$set": {f"required_fields.{field}": not bot["required_fields"].get(field, False)}})

    @classmethod
    def delete_bot(cls, bot_id: ObjectId) -> None:
        cls.bots.delete_one({"_id": bot_id})

    @classmethod
    def edit_caption(cls, bot_id: ObjectId, caption: str) -> None:
        cls.bots.update_one({"_id": bot_id}, {"$set": {"caption": caption}})

    @classmethod
    def add_question(cls, bot_id: ObjectId, question: str, answers: list[dict]) -> None:
        cls.bots.update_one({"_id": bot_id}, {"$push": {"faq": {"_id": ObjectId(), "question": question, "answers": answers}}})

    @classmethod
    def edit_question(cls, bot_id: ObjectId, question_id: ObjectId, question: str, answers: list[dict]) -> None:
        cls.bots.update_one({"_id": bot_id, "faq._id": question_id}, {"$set": {"faq.$.question": question, "faq.$.answers": answers}})

    @classmethod
    def delete_question(cls, bot_id: ObjectId, question_id: ObjectId) -> None:
        cls.bots.update_one({"_id": bot_id}, {"$pull": {"faq": {"_id": question_id}}})

    @classmethod
    def get_question(cls, bot_id: ObjectId, question_id: ObjectId) -> Optional[dict]:
        bot_obj = cls.bots.find_one({"_id": bot_id, "faq._id": question_id}, {"faq.$": 1})
        if bot_obj is None:
            return
        if bot_obj["faq"]:
            return bot_obj["faq"][0]

    @classmethod
    def delete_user(cls, bot_id: ObjectId, id: ObjectId) -> None:
        cls.bots.update_one({"_id": bot_id}, {"$pull": {"users": {"_id": id}}})

    @classmethod
    def delete_admin(cls, bot_id: ObjectId, admin_id: int) -> None:
        cls.bots.update_one({"_id": bot_id}, {"$pull": {"admins": admin_id}})
