from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram.ext import filters

from .bot import Bot

from .handlers import run_faq, edit_faq, \
    faq_ans, faq_add, faq_cancel, \
    message_handler


class CustomBot(Bot):
    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.handlers = [
            CommandHandler(["start", "help"], run_faq),
            CommandHandler("edit", edit_faq),

            CallbackQueryHandler(faq_ans, "^faq_ans"),
            CallbackQueryHandler(faq_add, "^faq_add"),
            CallbackQueryHandler(faq_cancel, "cancel"),

            MessageHandler(filters.ALL, message_handler),
        ]