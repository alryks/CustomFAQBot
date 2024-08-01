import asyncio

from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler
from telegram.ext import filters

from misc import callback

from db import BotsDb
from CustomBot.custom_bot import CustomBot
from state import bots

from config import BOT
from handlers import start, accept, deny, \
    bot, bot_page, bot_token, message_handler, cancel, \
    bot_private, bot_users, bot_delete, bot_back, \
    users_page, users_add, users_back, user, \
    edit_user_name, edit_job_title, edit_unit, edit_place, edit_phone, edit_email, user_back, \
    user_delete, user_admin, \
    user_unmerge, user_merge, user_merge_page, user_merge_back, users_merge, \
    bot_required, required_field, required_back


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
        CallbackQueryHandler(deny, "^deny"),

        CallbackQueryHandler(bot, "^bots_bot"),
        CallbackQueryHandler(bot_page, "^bots_page"),
        CallbackQueryHandler(bot_token, "bots_add"),
        CallbackQueryHandler(cancel, "cancel"),

        CallbackQueryHandler(bot_token, "^bot_edit"),
        CallbackQueryHandler(bot_private, "^bot_private"),
        CallbackQueryHandler(bot_users, "^bot_users"),
        CallbackQueryHandler(bot_delete, "^bot_delete"),
        CallbackQueryHandler(bot_back, "bot_back"),

        CallbackQueryHandler(users_page, "^users_page"),
        CallbackQueryHandler(users_add, "^users_add"),
        CallbackQueryHandler(users_back, "^users_back"),

        CallbackQueryHandler(edit_user_name, "^user_name"),
        CallbackQueryHandler(edit_job_title, "^user_job_title"),
        CallbackQueryHandler(edit_unit, "^user_unit"),
        CallbackQueryHandler(edit_place, "^user_place"),
        CallbackQueryHandler(edit_phone, "^user_phone"),
        CallbackQueryHandler(edit_email, "^user_email"),
        CallbackQueryHandler(user_admin, "^user_admin"),
        CallbackQueryHandler(user_delete, "^user_delete"),
        CallbackQueryHandler(user_back, "^user_back"),

        CallbackQueryHandler(user_unmerge, "^user_unmerge"),
        CallbackQueryHandler(user_merge_page, "^user_merge_page"),
        CallbackQueryHandler(user_merge_back, "^merge_back"),
        CallbackQueryHandler(user_merge, "^user_merge"),
        CallbackQueryHandler(users_merge, "^users_merge"),

        CallbackQueryHandler(bot_required, "^bot_required"),
        CallbackQueryHandler(required_back, "^required_back"),
        CallbackQueryHandler(required_field, "^required_"),

        CallbackQueryHandler(user, "^user"),

        MessageHandler(filters.ALL, message_handler)
    ]

    await BOT.run()

    await asyncio.Event().wait()

    await BOT.stop()

    for user_bot in bots.values():
        await user_bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
