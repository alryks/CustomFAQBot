from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler
from telegram.ext import filters

from misc import callback

from .bot import Bot

from .handlers import start, edit_faq, message_handler, \
    faq_ans, faq_ans_page, \
    faq_edit, faq_edit_page, \
    faq_add, faq_cancel, \
    question_edit, question_delete, question_back


class CustomBot(Bot):
    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.handlers = [
            CommandHandler(["start", "help"], start),
            CommandHandler("edit", edit_faq),

            CallbackQueryHandler(callback, "^callback"),

            CallbackQueryHandler(faq_ans_page, "^faq_ans_page"),
            CallbackQueryHandler(faq_ans, "^faq_ans"),

            CallbackQueryHandler(faq_edit_page, "^faq_edit_page"),
            CallbackQueryHandler(faq_edit, "^faq_edit"),

            CallbackQueryHandler(faq_add, "faq_add"),
            CallbackQueryHandler(faq_cancel, "cancel"),

            CallbackQueryHandler(question_edit, "^question_edit"),
            CallbackQueryHandler(question_delete, "^question_delete"),
            CallbackQueryHandler(question_back, "question_back"),

            MessageHandler(filters.ALL, message_handler),
        ]