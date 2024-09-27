from typing import Union, Optional

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


def faq(bot_faq: list, update: Update, edit: bool = False, page: int = 1) -> InlineKeyboardMarkup:
    buttons = []
    for i in range(len(bot_faq)):
        button = InlineKeyboardButton(f"{i + 1}", callback_data=f"faq {bot_faq[i]['_id']}")
        buttons.append(button)

    keyboard = pagination(buttons, page, f"faq",
                          horizontal=True, additional_buttons=1 + int(edit) * 2)

    if edit:
        keyboard.append([InlineKeyboardButton(Languages.kbd("edit_caption", update), callback_data=f"caption")])
        keyboard.append([InlineKeyboardButton(Languages.kbd("add_question", update), callback_data=f"faq_add")])
    keyboard.append([InlineKeyboardButton(Languages.kbd("cancel", update), callback_data="cancel")])

    return InlineKeyboardMarkup(keyboard)


def faq_edit(question_id: ObjectId, update: Update) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(Languages.kbd("edit", update), callback_data=f"question_edit {question_id}"),
         InlineKeyboardButton(Languages.kbd("delete", update), callback_data=f"question_delete {question_id}")],
        [InlineKeyboardButton(Languages.kbd("cancel", update), callback_data="question_cancel")]
    ])


def contacts(users: list, edit: bool, update: Update, page: int = 1, which: str = "user", user_id: Optional[ObjectId] = None) -> InlineKeyboardMarkup:
    buttons = []
    for i in range(len(users)):
        callback_data_user = f"{which} {users[i]['_id']}"
        if which == "similar":
            callback_data_user += f" {user_id}"
        button = InlineKeyboardButton(f"{i + 1}", callback_data=callback_data_user)
        buttons.append(button)

    pagination_callback = "contacts" if which == "user" else which
    keyboard = pagination(buttons, page, pagination_callback, horizontal=True, additional_buttons=1 + int(edit), additional_info=user_id if which == "similar" else "")

    if edit:
        keyboard.append([InlineKeyboardButton(Languages.kbd("add_user", update), callback_data="contacts_add")])

    if which == "similar" or which == "supervisors":
        keyboard.append([InlineKeyboardButton(Languages.kbd("to_user", update), callback_data=f"user {user_id}")])
    else:
        keyboard.append([InlineKeyboardButton(Languages.kbd("cancel", update), callback_data="cancel")])

    return InlineKeyboardMarkup(keyboard)


def user(user_obj: dict, admin: bool, update: Update) -> InlineKeyboardMarkup:
    user_id = user_obj["_id"]
    keyboard = [
        [
            InlineKeyboardButton(Languages.kbd("edit_user_name", update), callback_data=f"user_name {user_id}"),
            InlineKeyboardButton(Languages.kbd("edit_job_title", update), callback_data=f"user_job_title {user_id}")
        ],
        [
            InlineKeyboardButton(Languages.kbd("edit_unit", update),  callback_data=f"user_unit {user_id}"),
            InlineKeyboardButton(Languages.kbd("edit_place", update), callback_data=f"user_place {user_id}")
        ],
        [
            InlineKeyboardButton(Languages.kbd("edit_supervisor", update), callback_data=f"edit_supervisor {user_id}")
        ],
        [
            InlineKeyboardButton(Languages.kbd("edit_personal_phone", update), callback_data=f"user_personal_phone {user_id}"),
            InlineKeyboardButton(Languages.kbd("edit_work_phone", update), callback_data=f"user_work_phone {user_id}")
        ],
        [
            InlineKeyboardButton(Languages.kbd("edit_additional_number", update), callback_data=f"user_additional_number {user_id}"),
            InlineKeyboardButton(Languages.kbd("edit_email", update), callback_data=f"user_email {user_id}")
        ]
    ]
    # if admin:
    #     keyboard.append([
    #             InlineKeyboardButton(Languages.kbd("user_admin", update).format(admin="✅" if user_obj["is_admin"] else "❌"), callback_data=f"user_admin {user_id}")
    #     ])
    keyboard.extend([
        [
            InlineKeyboardButton(Languages.kbd("delete", update), callback_data=f"user_delete {user_id}")
        ],
        [
            InlineKeyboardButton(Languages.kbd("cancel", update), callback_data=f"user_cancel")
        ],
    ])

    return InlineKeyboardMarkup(keyboard)


def report(user_obj: dict, update: Update) -> InlineKeyboardMarkup:
    user_id = user_obj["_id"]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(Languages.kbd("report", update), callback_data=f"report {user_id}")],
    ])


def report_actions(report_obj: dict, update: Update) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(Languages.kbd("report_feedback", update), callback_data=f"report_feedback {report_obj['_id']}")],
        [InlineKeyboardButton(Languages.kbd("to_user", update), callback_data=f"user {report_obj['user']}")],
    ])


def report_feedback(report_obj: dict, update: Update) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(Languages.kbd("to_user", update), callback_data=f"user {report_obj['user']}")],
        [InlineKeyboardButton(Languages.kbd("cancel", update), callback_data="cancel")],
    ])


def confirm_delete(update: Update, user_obj: dict) -> InlineKeyboardMarkup:
    user_id = user_obj["_id"]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(Languages.kbd("delete", update), callback_data=f"user_confirm_delete {user_id}"),
         InlineKeyboardButton(Languages.kbd("cancel", update), callback_data="cancel")]
    ])


def reset(update: Update) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[Languages.btn("reset", update)], [Languages.btn("cancel", update)]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


def stop_answer(update: Update) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[Languages.btn("stop_answer", update)], [Languages.btn("cancel", update)]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


def accept_deny(user_id: Union[int, ObjectId]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅", callback_data=f"accept {user_id}"), InlineKeyboardButton("❌", callback_data=f"deny {user_id}")],
    ])