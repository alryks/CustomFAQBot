import asyncio

from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler
from telegram.ext import filters

from misc import callback

from config import BOT_TOKEN
from bot import Bot

from handlers import start, edit, cancel_command, message_handler, \
    accept, deny, \
    \
    faq_command, faq_page, \
    faq_add, faq_ans, \
    question_edit, question_delete, question_cancel, \
    \
    contacts_command, contacts_page, \
    contact, contacts_add, \
    \
    similar_page, similar_user, \
    \
    edit_contact_name, edit_job_title, edit_unit, edit_place, edit_phone, edit_email, \
    user_admin, user_delete, user_confirm_delete, user_cancel


async def main():
    BOT = Bot(BOT_TOKEN)

    BOT.handlers = [
        CommandHandler(["start", "help"], start),
        CommandHandler("edit", edit),
        CallbackQueryHandler(cancel_command, "cancel"),

        CallbackQueryHandler(accept, "^accept"),
        CallbackQueryHandler(deny, "^deny"),

        CommandHandler("faq", faq_command),
        CallbackQueryHandler(faq_page, "^faq_page"),

        CallbackQueryHandler(faq_add, "faq_add"),
        CallbackQueryHandler(faq_ans, "^faq"),

        CallbackQueryHandler(question_edit, "^question_edit"),
        CallbackQueryHandler(question_delete, "^question_delete"),
        CallbackQueryHandler(question_cancel, "question_cancel"),

        CommandHandler("contacts", contacts_command),
        CallbackQueryHandler(contacts_page, "^contacts_page"),
        CallbackQueryHandler(contacts_add, "contacts_add"),

        CallbackQueryHandler(similar_page, "^similar_page"),
        CallbackQueryHandler(similar_user, "^similar"),

        CallbackQueryHandler(edit_contact_name, "^user_name"),
        CallbackQueryHandler(edit_job_title, "^user_job_title"),
        CallbackQueryHandler(edit_unit, "^user_unit"),
        CallbackQueryHandler(edit_place, "^user_place"),
        CallbackQueryHandler(edit_phone, "^user_phone"),
        CallbackQueryHandler(edit_email, "^user_email"),
        CallbackQueryHandler(user_admin, "^user_admin"),
        CallbackQueryHandler(user_delete, "^user_delete"),
        CallbackQueryHandler(user_confirm_delete, "^user_confirm_delete"),
        CallbackQueryHandler(user_cancel, "^user_cancel"),

        CallbackQueryHandler(contact, "^user"),

        CallbackQueryHandler(callback, "^callback"),
        MessageHandler(filters.ALL, message_handler),
    ]

    BOT.commands = [
        "help",
        "faq",
        "contacts",
    ]

    await BOT.run()

    await asyncio.Event().wait()

    await BOT.stop()


if __name__ == "__main__":
    asyncio.run(main())
