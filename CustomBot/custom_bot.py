from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler
from telegram.ext import filters

from misc import callback

from .bot import Bot

from .handlers import start, edit, cancel_command, message_handler, \
    accept, deny, \
    \
    faq_command, faq_page, \
    edit_caption, faq_add, faq_ans, \
    question_edit, question_delete, question_cancel, \
    \
    contacts_command, contacts_page, \
    user, contacts_add, \
    edit_user_name, edit_job_title, edit_unit, edit_place, edit_phone, edit_email, \
    user_admin, user_delete, user_back, \
    user_unmerge, user_merge_page, user_merge_back, user_merge, users_merge


class CustomBot(Bot):
    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.handlers = [
            CommandHandler(["start", "help"], start),
            CommandHandler("edit", edit),
            CallbackQueryHandler(cancel_command, "cancel"),

            CallbackQueryHandler(accept, "^accept"),
            CallbackQueryHandler(deny, "^deny"),

            CommandHandler("faq", faq_command),
            CallbackQueryHandler(faq_page, "^faq_page"),

            CallbackQueryHandler(edit_caption, "caption"),
            CallbackQueryHandler(faq_add, "faq_add"),
            CallbackQueryHandler(faq_ans, "^faq"),

            CallbackQueryHandler(question_edit, "^question_edit"),
            CallbackQueryHandler(question_delete, "^question_delete"),
            CallbackQueryHandler(question_cancel, "question_cancel"),


            CommandHandler("contacts", contacts_command),
            CallbackQueryHandler(contacts_page, "^contacts_page"),
            CallbackQueryHandler(contacts_add, "contacts_add"),

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

            CallbackQueryHandler(user, "^user"),

            CallbackQueryHandler(callback, "^callback"),
            MessageHandler(filters.ALL, message_handler),
        ]

        self.commands = [
            "help",
            "faq",
            "contacts",
        ]
