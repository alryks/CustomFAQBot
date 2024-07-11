from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup

from bson import ObjectId

from config import ROWS_PER_PAGE, COLS_PER_PAGE


def cancel():
    return ReplyKeyboardMarkup([["✖️Cancel"]], resize_keyboard=True)


def bots(usernames: [(ObjectId, str)], page: int) -> InlineKeyboardMarkup:
    if len(usernames) <= ROWS_PER_PAGE - 2:
        max_buttons = len(usernames)
    else:
        max_buttons = ROWS_PER_PAGE - 3

    keyboard = []

    if max_buttons > 0:
        max_pages = (len(usernames) + max_buttons - 1) // max_buttons

        page = max(page, 1)
        page = min(page, max_pages)

        for i in range((page - 1) * max_buttons, min(page * max_buttons, len(usernames))):
            keyboard.append([InlineKeyboardButton(f"@{usernames[i][1]}", callback_data=f"bots_bot {usernames[i][0]}")])

        if max_pages > 1:
            pages_str = f"{page}/{max_pages}"
            keyboard.append([InlineKeyboardButton("⬅️", callback_data=f"bots_page {page - 1}"),
                             InlineKeyboardButton(pages_str, callback_data=f"callback {pages_str}"),
                             InlineKeyboardButton("➡️", callback_data=f"bots_page {page + 1}")])

    keyboard.append([InlineKeyboardButton("➕Add", callback_data="add_bot")])
    keyboard.append([InlineKeyboardButton("✖️Cancel", callback_data="cancel")])

    return InlineKeyboardMarkup(keyboard)


def bot(bot_obj: dict) -> InlineKeyboardMarkup:
    keyboard = []
    private = [InlineKeyboardButton(f"🔒Private: {'✅' if bot_obj['is_private'] else '❌'}", callback_data=f"bot_private {bot_obj['_id']}")]
    if bot_obj['is_private']:
        private.append(InlineKeyboardButton("👥Users", callback_data=f"bot_users {bot_obj['_id']}"))
    keyboard.append(private)
    keyboard.append([InlineKeyboardButton("👤Admins", callback_data=f"bot_admins {bot_obj['_id']}")])
    keyboard.append([InlineKeyboardButton("🗑️Delete", callback_data=f"bot_delete {bot_obj['_id']}")])
    keyboard.append([InlineKeyboardButton("🔙Back", callback_data="bot_back")])

    return InlineKeyboardMarkup(keyboard)
