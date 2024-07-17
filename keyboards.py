from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup

from telegram.ext import ExtBot

from bson import ObjectId

from misc import pagination


def cancel():
    return ReplyKeyboardMarkup([["✖️Cancel"]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


def bots(usernames: [(ObjectId, str)], page: int) -> InlineKeyboardMarkup:
    buttons = []
    for username in usernames:
        buttons.append(InlineKeyboardButton(f"@{username[1]}", callback_data=f"bots_bot {username[0]}"))

    keyboard = pagination(buttons, page, "bots", additional_buttons=2)

    keyboard.append([InlineKeyboardButton("➕Add", callback_data="bots_add")])
    keyboard.append([InlineKeyboardButton("✖️Cancel", callback_data="cancel")])

    return InlineKeyboardMarkup(keyboard)


def bot(bot_obj: dict) -> InlineKeyboardMarkup:
    keyboard = []
    keyboard.append([InlineKeyboardButton("🔑Edit Token", callback_data=f"bot_edit {bot_obj['_id']}")])
    private = [InlineKeyboardButton(f"🔒Private: {'✅' if bot_obj['is_private'] else '❌'}", callback_data=f"bot_private {bot_obj['_id']}")]
    if bot_obj['is_private']:
        private.append(InlineKeyboardButton("👥Users", callback_data=f"bot_users {bot_obj['_id']}"))
    keyboard.append(private)
    keyboard.append([InlineKeyboardButton("🚨Admins", callback_data=f"bot_admins {bot_obj['_id']}")])
    keyboard.append([InlineKeyboardButton("🗑️Delete", callback_data=f"bot_delete {bot_obj['_id']}")])
    keyboard.append([InlineKeyboardButton("🔙Back", callback_data="bot_back")])

    return InlineKeyboardMarkup(keyboard)


async def users(bot_obj: dict, bot: ExtBot) -> InlineKeyboardMarkup:
    keyboard = []
    for bot_user in bot_obj['users']:
        chat = await bot.get_chat(bot_user)
        name = chat.full_name + (f" @{chat.username}" if chat.username else "")
        keyboard.append([InlineKeyboardButton(name, callback_data=f"callback {name}"),
                         InlineKeyboardButton("🗑️", callback_data=f"user_delete {bot_obj['_id']} {bot_user}")])

    keyboard.append([InlineKeyboardButton("🔙Back", callback_data=f"users_back {bot_obj['_id']}")])

    return InlineKeyboardMarkup(keyboard)


async def admins(bot_obj: dict, user: int, bot: ExtBot) -> InlineKeyboardMarkup:
    keyboard = []
    for admin in bot_obj['admins']:
        chat = await bot.get_chat(admin)
        name = chat.full_name + (f" @{chat.username}" if chat.username else "")
        row = [InlineKeyboardButton(name, callback_data=f"callback {name}")]
        if admin != user:
            row.append(InlineKeyboardButton("🗑️", callback_data=f"admin_delete {bot_obj['_id']} {admin}"))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙Back", callback_data=f"admins_back {bot_obj['_id']}")])

    return InlineKeyboardMarkup(keyboard)