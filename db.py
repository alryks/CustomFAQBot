import pymongo
from pymongo.errors import DuplicateKeyError

from bson import ObjectId

from telegram.ext import Application

from typing import Optional

from config import DB
from state import State, bots


class BotsDb:
    bots: pymongo.collection.Collection = DB.bots
    bots.create_index("bot_id", unique=True)

    @classmethod
    def is_admin(cls, bot_id: ObjectId, user_id: int) -> bool:
        return cls.bots.find_one({"_id": bot_id, "admins": user_id}) is not None

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
    def add_bot(cls, bot_id: int, bot_token: str, admin: int) -> Optional[ObjectId]:
        try:
            return cls.bots.insert_one({"bot_id": bot_id,
                                        "bot_token": bot_token,
                                        "admins": [admin],
                                        "is_private": False,
                                        "allowed_users": [],
                                        "faq": [],
                                        }).inserted_id
        except DuplicateKeyError:
            return None

    @classmethod
    def edit_token(cls, bot_id: ObjectId, bot_token: str) -> None:
        cls.bots.update_one({"_id": bot_id}, {"$set": {"bot_token": bot_token}})

    @classmethod
    def toggle_private(cls, bot_id: ObjectId) -> None:
        bot = cls.bots.find_one({"_id": bot_id})
        if bot is None:
            return
        cls.bots.update_one({"_id": bot_id}, {"$set": {"is_private": not bot["is_private"]}})

    @classmethod
    def delete_bot(cls, bot_id: ObjectId) -> None:
        cls.bots.delete_one({"_id": bot_id})

    @classmethod
    def add_faq(cls, bot_id: ObjectId, question: str, chat_id: int, message_id: int) -> None:
        cls.bots.update_one({"_id": bot_id}, {"$push": {"faq": {"question": question, "answer": {"chat_id": chat_id, "message_id": message_id}}}})
