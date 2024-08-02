from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup

from bson import ObjectId

from misc import pagination

from lang import Languages


def cancel(update: Update) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[Languages.btn("cancel", update)]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


def bots(usernames: [(ObjectId, str)], page: int, update: Update) -> InlineKeyboardMarkup:
    buttons = []
    for username in usernames:
        buttons.append(InlineKeyboardButton(f"@{username[1]}", callback_data=f"bots_bot {username[0]}"))

    keyboard = pagination(buttons, page, "bots", additional_buttons=2)

    keyboard.append([InlineKeyboardButton(Languages.kbd("add", update), callback_data="bots_add")])
    keyboard.append([InlineKeyboardButton(Languages.kbd("cancel", update), callback_data="cancel")])

    return InlineKeyboardMarkup(keyboard)


def bot(bot_obj: dict, update: Update) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(Languages.kbd("edit_token", update),
                                      callback_data=f"bot_edit {bot_obj['_id']}")],
                [InlineKeyboardButton(Languages.kbd("private", update).format(
                    private="✅" if bot_obj["is_private"] else "❌"),
                                      callback_data=f"bot_private {bot_obj['_id']}")],
                [InlineKeyboardButton(Languages.kbd("required", update),
                                      callback_data=f"bot_required {bot_obj['_id']}")],
                [InlineKeyboardButton(Languages.kbd("delete", update),
                                      callback_data=f"bot_delete {bot_obj['_id']}")],
                [InlineKeyboardButton(Languages.kbd("back", update),
                                      callback_data="bot_back")]]

    return InlineKeyboardMarkup(keyboard)


def required(bot_obj: dict, update: Update) -> InlineKeyboardMarkup:
    keyboard = []
    row = []
    for field, value in bot_obj["required_fields"].items():
        row.append(InlineKeyboardButton(Languages.kbd(f"required_{field}", update).format(status="✅" if value else "❌"), callback_data=f"required_{field} {bot_obj['_id']}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(Languages.kbd("back", update), callback_data=f"required_back {bot_obj['_id']}")])

    return InlineKeyboardMarkup(keyboard)
