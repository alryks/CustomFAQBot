import asyncio

from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler
from telegram.ext import filters

from db import BotsDb
from CustomBot.custom_bot import CustomBot
from state import bots

from config import BOT
from handlers import start, callback, accept, \
    bot, bot_page, bot_token, message_handler, cancel, \
    bot_private, bot_users, bot_admins, bot_delete, bot_back, \
    user_delete, users_back, admin_delete, admins_back


async def main():
    for bot_obj in BotsDb.get_bots():
        user_bot = CustomBot(bot_obj["bot_token"])
        if not await user_bot.run():
            continue
        bots[bot_obj["_id"]] = user_bot

    BOT.handlers = [
        CommandHandler(["start", "help"], start),
        CallbackQueryHandler(callback, "^callback"),

        CallbackQueryHandler(accept, "^accept"),

        CallbackQueryHandler(bot, "^bots_bot"),
        CallbackQueryHandler(bot_page, "^bots_page"),
        CallbackQueryHandler(bot_token, "bots_add"),
        MessageHandler(filters.ALL, message_handler),
        CallbackQueryHandler(cancel, "cancel"),

        CallbackQueryHandler(bot_token, "^bot_edit"),
        CallbackQueryHandler(bot_private, "^bot_private"),
        CallbackQueryHandler(bot_users, "^bot_users"),
        CallbackQueryHandler(bot_admins, "^bot_admins"),
        CallbackQueryHandler(bot_delete, "^bot_delete"),
        CallbackQueryHandler(bot_back, "bot_back"),

        CallbackQueryHandler(user_delete, "^user_delete"),
        CallbackQueryHandler(users_back, "^users_back"),
        CallbackQueryHandler(admin_delete, "^admin_delete"),
        CallbackQueryHandler(admins_back, "^admins_back"),
    ]

    await BOT.run()

    await asyncio.Event().wait()

    await BOT.stop()

    for user_bot in bots.values():
        await user_bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
