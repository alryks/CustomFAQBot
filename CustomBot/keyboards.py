from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup

from bson import ObjectId

from misc import pagination

from lang import Languages


def faq(bot_faq: list, update: Update, edit: bool = False, page: int = 1) -> InlineKeyboardMarkup:
    question_type = "edit" if edit else "ans"
    buttons = []
    for i in range(len(bot_faq)):
        button = InlineKeyboardButton(f"{i + 1}", callback_data=f"faq_{question_type} {bot_faq[i]['_id']}")
        buttons.append(button)

    keyboard = pagination(buttons, page, f"faq_{question_type}",
                          horizontal=True, additional_buttons=1 + int(edit))

    if edit:
        keyboard.append([InlineKeyboardButton(Languages.kbd("edit_caption", update), callback_data=f"caption")])
        keyboard.append([InlineKeyboardButton(Languages.kbd("add_question", update), callback_data=f"faq_add")])
    keyboard.append([InlineKeyboardButton(Languages.kbd("cancel", update), callback_data="cancel")])

    return InlineKeyboardMarkup(keyboard)


def reset_caption(update: Update) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[Languages.btn("reset_caption", update)], [Languages.btn("cancel", update)]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


def stop_answer(update: Update) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[Languages.btn("stop_answer", update)], [Languages.btn("cancel", update)]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


def faq_edit(question_id: ObjectId, update: Update) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(Languages.kbd("edit", update), callback_data=f"question_edit {question_id}"),
         InlineKeyboardButton(Languages.kbd("delete", update), callback_data=f"question_delete {question_id}")],
        [InlineKeyboardButton(Languages.kbd("back", update), callback_data="question_back")]
    ])


def accept_deny(bot_obj: dict, user_id: int, is_admin=False) -> InlineKeyboardMarkup:
    access_type = "admin" if is_admin else "user"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅", callback_data=f"accept_{access_type} {bot_obj['_id']} {user_id}"), InlineKeyboardButton("❌", callback_data="cancel")]
    ])