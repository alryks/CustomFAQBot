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
        # get bot ids, where users.tg_id == user_id and users.is_admin == True
        bot_ids = cls.bots.distinct("_id", {"users.tg_id": user_id, "users.is_admin": True})
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
    def add_bot(cls, bot_id: int, bot_token: str, admin: int) -> Optional[ObjectId]:
        try:
            bot_obj_id = cls.bots.insert_one({"bot_id": bot_id,
                                        "bot_token": bot_token,
                                        "is_private": False,
                                        "users": [],
                                        "caption": "",
                                        "faq": [],
                                        }).inserted_id
            cls.add_user_with_id(bot_obj_id, admin, is_admin=True)

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
        users = cls.bots.find_one({"_id": bot_id, "users.tg_id": user_id, "users.is_admin": True}, {"users.$": 1})
        if users is not None and users.get("users"):
            return True
        return False

    @classmethod
    def get_admin_ids(cls, bot_id: ObjectId) -> [dict]:
        bot = cls.bots.find_one({"_id": bot_id, "users.is_admin": True}, {"users.$": 1})
        if bot is None:
            return []
        users = bot.get("users", [])
        return [user.get("tg_id", 0) for user in users]

    @classmethod
    def is_user(cls, bot_id: ObjectId, user_id: int) -> bool:
        # get all users from bot_id, where is_temp is unset
        bot = cls.bots.find_one({"_id": bot_id})
        users_bot = cls.bots.find_one({"_id": bot_id, "users.is_temp": {"$exists": False}})
        if users_bot is None:
            return False
        users = users_bot.get("users", [])
        user_ids = [user.get("tg_id", 0) for user in users]
        print(user_ids)
        admin_ids = cls.get_admin_ids(bot_id)
        print(admin_ids)
        if bot and (not bot.get("is_private", False) or
                    user_id in user_ids or
                    user_id in admin_ids):
            return True
        return False

    @classmethod
    def is_temp_user_id(cls, bot_id: ObjectId, user_id: int) -> bool:
        bot = cls.bots.find_one({"_id": bot_id, "users.tg_id": user_id, "users.is_temp": True})
        if bot is not None:
            return True
        return False

    @classmethod
    def is_temp_user(cls, bot_id: ObjectId, user_id: ObjectId) -> bool:
        bot = cls.bots.find_one({"_id": bot_id, "users._id": user_id, "users.is_temp": True})
        if bot is not None:
            return True
        return False

    @classmethod
    def add_user_with_id(cls, bot_id: ObjectId, user_id: int, is_admin: bool = False) -> None:
        for user in cls.bots.find_one({"_id": bot_id}).get("users", []):
            if user.get("tg_id", 0) == user_id:
                return
        cls.bots.update_one({"_id": bot_id}, {"$push": {"users": {
            "_id": ObjectId(),
            "tg_id": user_id,
            "is_admin": is_admin,
        }}})

    @classmethod
    def add_user_with_data(cls, bot_id: ObjectId, name: str = "", job_title: str = "", unit: str = "", place: str = "", phone: str = "", email: str = "") -> ObjectId:
        user_id = ObjectId()
        cls.bots.update_one({"_id": bot_id}, {"$addToSet": {"users": {
            "_id": user_id,
            "tg_id": 0,
            "is_admin": False,
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
            "is_admin": False,
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
    def toggle_admin(cls, bot_id: ObjectId, user_id: ObjectId) -> None:
        users = cls.bots.find_one({"_id": bot_id, "users._id": user_id}, {"users.$": 1}).get("users", [])
        if not users:
            return
        cls.bots.update_one({"_id": bot_id, "users._id": user_id}, {"$set": {"users.$.is_admin": not users[0].get("is_admin", False)}})

    @classmethod
    def get_users_to_merge(cls, bot_id: ObjectId) -> [dict]:
        bot = cls.bots.find_one({"_id": bot_id})
        users = bot.get("users", [])
        users = [user for user in users if user.get("tg_id", 0) != 0 and user.get("is_temp", False) is False]
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
