import asyncio

from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler
from telegram.ext import filters

from misc import callback

from db import BotsDb
from CustomBot.custom_bot import CustomBot
from state import bots

from config import BOT_TOKEN
from CustomBot.bot import Bot

from handlers import start, \
    bot, bot_page, bot_token, message_handler, cancel, \
    bot_private, bot_delete, bot_back, \
    bot_required, required_field, required_back


async def main():
    for bot_obj in BotsDb.get_bots():
        user_bot = CustomBot(bot_obj["bot_token"])
        if not await user_bot.run():
            continue
        bots[bot_obj["_id"]] = user_bot

    BOT = Bot(BOT_TOKEN)

    BOT.handlers = [
        CommandHandler(["start", "help"], start),
        CallbackQueryHandler(callback, "^callback"),

        CallbackQueryHandler(bot, "^bots_bot"),
        CallbackQueryHandler(bot_page, "^bots_page"),
        CallbackQueryHandler(bot_token, "bots_add"),
        CallbackQueryHandler(cancel, "cancel"),

        CallbackQueryHandler(bot_token, "^bot_edit"),
        CallbackQueryHandler(bot_private, "^bot_private"),
        CallbackQueryHandler(bot_delete, "^bot_delete"),
        CallbackQueryHandler(bot_back, "bot_back"),

        CallbackQueryHandler(bot_required, "^bot_required"),
        CallbackQueryHandler(required_back, "^required_back"),
        CallbackQueryHandler(required_field, "^required_"),

        MessageHandler(filters.ALL, message_handler)
    ]

    await BOT.run(start_command=True)

    await asyncio.Event().wait()

    await BOT.stop()

    for user_bot in bots.values():
        await user_bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
