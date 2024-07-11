import asyncio

from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler
from telegram.ext import filters

from db import BotsDb
from CustomBot.custom_bot import CustomBot
from state import bots

from config import BOT
from handlers import start, callback, \
    bot, bot_page, add_bot, message_handler, cancel, \
    bot_private, bot_users, bot_admins, bot_delete, bot_back


async def main():
    for bot_obj in BotsDb.get_bots():
        user_bot = CustomBot(bot_obj["bot_token"])
        if not await user_bot.run():
            continue
        bots[bot_obj["_id"]] = user_bot

    BOT.handlers = [
        CommandHandler(["start", "help"], start),
        CallbackQueryHandler(callback, "^callback"),

        CallbackQueryHandler(bot, "^bots_bot"),
        CallbackQueryHandler(bot_page, "^bots_page"),
        CallbackQueryHandler(add_bot, "add_bot"),
        MessageHandler(filters.ALL, message_handler),
        CallbackQueryHandler(cancel, "cancel"),

        CallbackQueryHandler(bot_private, "^bot_private"),
        CallbackQueryHandler(bot_users, "^bot_users"),
        CallbackQueryHandler(bot_admins, "^bot_admins"),
        CallbackQueryHandler(bot_delete, "^bot_delete"),
        CallbackQueryHandler(bot_back, "bot_back"),
    ]

    await BOT.run()

    await asyncio.Event().wait()

    await BOT.stop()

    for user_bot in bots.values():
        await user_bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
