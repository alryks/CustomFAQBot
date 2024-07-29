from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup

from telegram.ext import ExtBot

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
    keyboard = []
    keyboard.append([InlineKeyboardButton(Languages.kbd("edit_token", update), callback_data=f"bot_edit {bot_obj['_id']}")])
    private = [InlineKeyboardButton(Languages.kbd("private", update).format(private="✅" if bot_obj["is_private"] else "❌"), callback_data=f"bot_private {bot_obj['_id']}")]
    if bot_obj['is_private']:
        private.append(InlineKeyboardButton(Languages.kbd("users", update), callback_data=f"bot_users {bot_obj['_id']}"))
    keyboard.append(private)
    keyboard.append([InlineKeyboardButton(Languages.kbd("admins", update), callback_data=f"bot_admins {bot_obj['_id']}")])
    keyboard.append([InlineKeyboardButton(Languages.kbd("required", update), callback_data=f"bot_required {bot_obj['_id']}")])
    keyboard.append([InlineKeyboardButton(Languages.kbd("delete", update), callback_data=f"bot_delete {bot_obj['_id']}")])
    keyboard.append([InlineKeyboardButton(Languages.kbd("back", update), callback_data="bot_back")])

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


async def users(bot_obj: dict, bot: ExtBot, page: int, update: Update) -> InlineKeyboardMarkup:
    buttons = []
    for bot_user in bot_obj["users"]:
        if bot_user.get("name", "") != "":
            name = bot_user["name"]
        else:
            chat = await bot.get_chat(bot_user["tg_id"])
            name = chat.full_name + (f" @{chat.username}" if chat.username else "")
        buttons.append([InlineKeyboardButton(name, callback_data=f"user {bot_obj['_id']} {bot_user['_id']}"),
                         InlineKeyboardButton("🗑️", callback_data=f"user_delete {bot_obj['_id']} {bot_user['_id']}")])

    keyboard = pagination(buttons, page, "users", additional_buttons=2, additional_info=str(bot_obj['_id']))

    keyboard.append([InlineKeyboardButton(Languages.kbd("add_user", update), callback_data=f"users_add {bot_obj['_id']}")])
    keyboard.append([InlineKeyboardButton(Languages.kbd("back", update), callback_data=f"users_back {bot_obj['_id']}")])

    return InlineKeyboardMarkup(keyboard)


def user(bot_id: ObjectId, user_id: ObjectId, update: Update, is_merge: bool) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(Languages.kbd("edit_user_name", update), callback_data=f"user_name {bot_id} {user_id}"),
            InlineKeyboardButton(Languages.kbd("edit_job_title", update), callback_data=f"user_job_title {bot_id} {user_id}")
        ],
        [
            InlineKeyboardButton(Languages.kbd("edit_unit", update),  callback_data=f"user_unit {bot_id} {user_id}"),
            InlineKeyboardButton(Languages.kbd("edit_place", update), callback_data=f"user_place {bot_id} {user_id}")
        ],
        [
            InlineKeyboardButton(Languages.kbd("edit_phone", update), callback_data=f"user_phone {bot_id} {user_id}"),
            InlineKeyboardButton(Languages.kbd("edit_email", update), callback_data=f"user_email {bot_id} {user_id}")
        ],
        [
            InlineKeyboardButton(Languages.kbd("merge", update), callback_data=f"user_merge {bot_id} {user_id}") if is_merge else InlineKeyboardButton(Languages.kbd("unmerge", update), callback_data=f"user_unmerge {bot_id} {user_id}")
        ],
        [
            InlineKeyboardButton(Languages.kbd("back", update), callback_data=f"user_back {bot_id}")
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


async def user_merge(bot_id: ObjectId, user_id: ObjectId, bot: ExtBot, users: [dict], page: int, update: Update) -> InlineKeyboardMarkup:
    buttons = []
    for bot_user in users:
        if bot_user.get("name", "") != "":
            name = bot_user["name"]
        else:
            chat = await bot.get_chat(bot_user["tg_id"])
            name = chat.full_name + (f" @{chat.username}" if chat.username else "")
        buttons.append([InlineKeyboardButton(name, callback_data=f"users_merge {bot_id} {bot_user['_id']}")])

    keyboard = pagination(buttons, page, "user_merge", additional_buttons=1, additional_info=str(bot_id))

    keyboard.append([InlineKeyboardButton(Languages.kbd("back", update), callback_data=f"merge_back {bot_id} {user_id}")])

    return InlineKeyboardMarkup(keyboard)


def reset(update: Update) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[Languages.btn("reset", update)], [Languages.btn("cancel", update)]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


async def admins(bot_obj: dict, user: int, bot: ExtBot, update: Update) -> InlineKeyboardMarkup:
    keyboard = []
    for admin in bot_obj['admins']:
        chat = await bot.get_chat(admin)
        name = chat.full_name + (f" @{chat.username}" if chat.username else "")
        row = [InlineKeyboardButton(name, callback_data=f"callback {name}")]
        if admin != user:
            row.append(InlineKeyboardButton("🗑️", callback_data=f"admin_delete {bot_obj['_id']} {admin}"))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(Languages.kbd("back", update), callback_data=f"admins_back {bot_obj['_id']}")])

    return InlineKeyboardMarkup(keyboard)