import pymongo
from pymongo.errors import DuplicateKeyError

from bson import ObjectId

from telegram.ext import Application

from typing import Union

from config import DB
from state import State, bots


class BotsDb:
    bots: pymongo.collection.Collection = DB.bots
    bots.create_index("bot_token", unique=True)

    @classmethod
    def is_admin(cls, bot_id: ObjectId, user_id: int) -> bool:
        return cls.bots.find_one(
            {"_id": bot_id, "admins": user_id}) is not None

    @classmethod
    def get_bot(cls, bot_id: ObjectId) -> dict:
        return cls.bots.find_one({"_id": bot_id})

    @classmethod
    def get_bot_by_token(cls, bot_token: str) -> dict:
        return cls.bots.find_one({"bot_token": bot_token})

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
                bot_user = await app.bot.get_me()
                usernames.append((bot_id, bot_user.username))
            except:
                continue
        return usernames

    @classmethod
    def add_bot(cls, bot_token: str, admin: int) -> Union[ObjectId, None]:
        try:
            return cls.bots.insert_one({"bot_token": bot_token,
                                        "admins": [admin],
                                        "is_private": False,
                                        "allowed_users": [],
                                        "faq": [],
                                        }).inserted_id
        except DuplicateKeyError:
            return None

    @classmethod
    def delete_bot(cls, bot_id: ObjectId) -> None:
        cls.bots.delete_one({"_id": bot_id})

    @classmethod
    def add_faq(cls, bot_id: ObjectId, question: str, chat_id: int, message_id: int) -> None:
        cls.bots.update_one({"_id": bot_id}, {"$push": {"faq": {"question": question, "answer": {"chat_id": chat_id, "message_id": message_id}}}})
