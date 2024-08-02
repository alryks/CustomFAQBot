from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from bson import ObjectId

from config import PARSE_MODE

from . import keyboards
from keyboards import cancel

from db import BotsDb

from .state import State

from misc import create_faq, filter_faq, \
    create_contacts, search_contacts, filter_contacts, sort_contacts, \
    get_first_required_field, user_info, check_phone, check_email

from lang import Languages


async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    if BotsDb.is_user(bot_obj["_id"], update.effective_user.id):
        return True

    if BotsDb.is_temp_user_id(bot_obj["_id"], update.effective_user.id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("already_requested", update).format(bot_name=context.bot.bot.username),
            parse_mode=PARSE_MODE,
        )
        return False

    first_field = get_first_required_field(bot_obj)

    if not first_field:
        user_id = BotsDb.add_temp_user(bot_obj["_id"], update.effective_user.id)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("not_user_request", update),
            parse_mode=PARSE_MODE,
        )

        user_obj = BotsDb.get_user(bot_obj["_id"], user_id)

        for admin in BotsDb.get_admin_ids(bot_obj["_id"]):
            await context.bot.send_message(
                chat_id=admin,
                text=Languages.msg("request_user", update).format(data=user_info(user_obj, update, context.bot)),
                reply_markup=keyboards.accept_deny(bot_obj, user_id),
                parse_mode=PARSE_MODE,
            )
        return False

    context.user_data["state"] = State[first_field.upper()].name

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("register", update),
        parse_mode=PARSE_MODE,
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_" + first_field, update),
        reply_markup=cancel(update),
        parse_mode=PARSE_MODE,
    )

    return False


async def check_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
        return True

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("not_admin", update),
        parse_mode=PARSE_MODE,
    )

    return False


async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    if not BotsDb.is_admin(bot_obj["_id"], update.effective_user.id):
        context.user_data["edit"] = False
        return

    user_id = ObjectId(update.callback_query.data.split(" ")[1])

    if BotsDb.is_temp_user(bot_obj["_id"], user_id):
        BotsDb.set_perm_user(bot_obj["_id"], user_id)
        tg_id = BotsDb.get_user(bot_obj["_id"], user_id).get("tg_id", 0)
        await context.bot.send_message(
            chat_id=tg_id,
            text=Languages.msg("user_accepted", update),
            parse_mode=PARSE_MODE,
        )

    context.user_data["edit"] = True

    await user(update, context)


async def deny(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    if not BotsDb.is_admin(bot_obj["_id"], update.effective_user.id):
        context.user_data["edit"] = False
        return

    user_id = ObjectId(update.callback_query.data.split(" ")[1])

    if BotsDb.is_temp_user(bot_obj["_id"], user_id):
        tg_id = BotsDb.get_user(bot_obj["_id"], user_id).get("tg_id", 0)
        await context.bot.send_message(
            chat_id=tg_id,
            text=Languages.msg("user_denied", update),
            parse_mode=PARSE_MODE,
        )
        BotsDb.delete_temp_user(bot_obj["_id"], user_id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search"] = None
    context.user_data["state"] = State.IDLE.name

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("start", update),
        parse_mode=PARSE_MODE,
    )

    await check_user(update, context)


async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update, context):
        return

    context.user_data["edit"] = not context.user_data.get("edit", False)

    if context.user_data["edit"]:
        message = Languages.msg("edit_true", update)
    else:
        message = Languages.msg("edit_false", update)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode=PARSE_MODE,
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )


async def delete_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    delete_message_ids = context.user_data.get("delete_message_ids")
    if delete_message_ids is not None:
        for delete_message_id in delete_message_ids:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=delete_message_id
                )
            except:
                pass

    context.user_data["delete_message_ids"] = []


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE, delete=False, page=1) -> None:
    context.user_data["state"] = State.FAQ.name

    if not await check_user(update, context):
        return

    if context.user_data.get("edit", False):
        if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
            context.user_data["edit"] = False

    search = context.user_data.get("search")
    if search is None:
        search = ""

    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    bot_faq = filter_faq(bot_obj["faq"], search)

    text = create_faq(bot_faq, context.bot.bot.username, bot_obj.get("caption", ""), update, page)

    if delete:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboards.faq(bot_faq, update, context.user_data.get("edit", False), page),
        parse_mode=PARSE_MODE,
    )


async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search"] = None
    await faq(update, context)


async def faq_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await faq(update, context, delete=True, page=int(update.callback_query.data.split(" ")[1]))


async def faq_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
        context.user_data["edit"] = False
        await faq(update, context, delete=True)
        return

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_question", update),
        reply_markup=cancel(update),
        parse_mode=PARSE_MODE,
    )

    context.user_data["state"] = State.ADD_QUESTION.name


async def faq_ans(update: Update, context: ContextTypes.DEFAULT_TYPE, question_id: Optional[ObjectId] = None) -> None:
    if not await check_user(update, context):
        return

    if question_id is None:
        question_id = ObjectId(update.callback_query.data.split(" ")[1])

    question = BotsDb.get_question(BotsDb.get_bot_by_id(context.bot.id)["_id"], question_id)
    if question is None:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id,
        )
        await faq(update, context)
        return
    answers = question["answers"]

    await delete_messages(update, context)

    if context.user_data.get("edit", False):
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("current_question", update).format(question=question["question"]),
            parse_mode=PARSE_MODE,
        )
        context.user_data["delete_message_ids"].append(message.message_id)

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("current_answers", update),
            parse_mode=PARSE_MODE,
        )
        context.user_data["delete_message_ids"].append(message.message_id)

    for answer in answers:
        message = await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=answer["chat_id"],
            message_id=answer["message_id"],
        )
        context.user_data["delete_message_ids"].append(message.message_id)

    if context.user_data.get("edit", False):
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("question_action", update),
            reply_markup=keyboards.faq_edit(question["_id"], update),
            parse_mode=PARSE_MODE,
        )
        context.user_data["delete_message_ids"].append(message.message_id)

    if update.callback_query:
        await update.callback_query.answer(
            text=Languages.msg("answer_sent", update),
        )


async def question_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
        context.user_data["edit"] = False

        await delete_messages(update, context)

        await faq(update, context)
        return

    context.user_data["question_id"] = ObjectId(update.callback_query.data.split(" ")[1])
    context.user_data["state"] = State.EDIT_QUESTION.name

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_new_question", update),
        reply_markup=cancel(update),
        parse_mode=PARSE_MODE,
    )


async def question_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
        context.user_data["edit"] = False

        await delete_messages(update, context)

        await faq(update, context)
        return

    question_id = ObjectId(update.callback_query.data.split(" ")[1])
    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    BotsDb.delete_question(bot_obj["_id"], question_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("question_deleted", update),
        parse_mode=PARSE_MODE,
    )

    await delete_messages(update, context)

    await faq(update, context)


async def question_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await delete_messages(update, context)

    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
        context.user_data["edit"] = False
        await faq(update, context)
        return


async def edit_caption(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
        context.user_data["edit"] = False
        await faq(update, context, delete=True)
        return

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_caption", update).format(bot_username=context.bot.bot.username),
        reply_markup=keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )

    context.user_data["state"] = State.EDIT_CAPTION.name


async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE, delete: bool = False, page: int = 1) -> None:
    context.user_data["state"] = State.CONTACTS.name

    if not await check_user(update, context):
        return

    if context.user_data.get("edit", False):
        if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
            context.user_data["edit"] = False

    search = context.user_data.get("search")
    if search is None:
        search = ""

    bot_obj = BotsDb.get_bot_by_id(context.bot.id)

    bot_contacts = search_contacts(bot_obj["users"], search)
    if not context.user_data.get("edit", False):
        bot_contacts = filter_contacts(bot_contacts)
    bot_contacts = sort_contacts(bot_contacts)

    text = await create_contacts(bot_contacts, context.bot, update, page)

    if delete:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboards.contacts(bot_contacts, context.user_data.get("edit", False), update, page),
        parse_mode=PARSE_MODE,
    )


async def contacts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search"] = None
    await contacts(update, context)


async def contacts_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await contacts(update, context, delete=True, page=int(update.callback_query.data.split(" ")[1]))


async def contacts_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
        context.user_data["edit"] = False
        await contacts(update, context, delete=True)
        return

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    first_field = get_first_required_field(BotsDb.get_bot_by_id(context.bot.id))

    context.user_data["state"] = State[first_field.upper()].name
    context.user_data["user"] = {}

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_" + first_field, update),
        reply_markup=cancel(update),
        parse_mode=PARSE_MODE,
    )


async def user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: Optional[ObjectId] = None) -> None:
    if not await check_user(update, context):
        return

    if context.user_data.get("edit", False):
        if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
            context.user_data["edit"] = False

    if user_id is None:
        user_id = ObjectId(update.callback_query.data.split(" ")[1])
    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    user_obj = BotsDb.get_user(bot_obj["_id"], user_id)

    await delete_messages(update, context)

    is_merge = True if user_obj.get("tg_id", 0) == 0 else False

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=await user_info(user_obj, update, context.bot),
        reply_markup=keyboards.user(user_obj, user_obj["tg_id"] != update.effective_user.id, update, is_merge) if context.user_data.get("edit", False) else None,
        parse_mode=PARSE_MODE,
    )
    context.user_data["delete_message_ids"].append(message.message_id)

    if update.callback_query:
        await update.callback_query.answer(
            text=Languages.msg("answer_sent", update),
        )


async def edit_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
        context.user_data["edit"] = False
        await user(update, context)
        return

    context.user_data["state"] = State.EDIT_NAME.name
    context.user_data["user_id"] = ObjectId(update.callback_query.data.split(" ")[1])

    is_required = BotsDb.get_bot_by_id(context.bot.id).get("required_fields", {}).get("name", False)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_name", update),
        reply_markup=cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )


async def edit_job_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"],
                           update.effective_user.id):
        context.user_data["edit"] = False
        await user(update, context)
        return

    context.user_data["state"] = State.EDIT_JOB.name
    context.user_data["user_id"] = ObjectId(
        update.callback_query.data.split(" ")[1])

    is_required = BotsDb.get_bot_by_id(context.bot.id).get("required_fields", {}).get("name", False)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_job_title", update),
        reply_markup=cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )


async def edit_unit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"],
                           update.effective_user.id):
        context.user_data["edit"] = False
        await user(update, context)
        return

    context.user_data["state"] = State.EDIT_UNIT.name
    context.user_data["user_id"] = ObjectId(
        update.callback_query.data.split(" ")[1])

    is_required = BotsDb.get_bot_by_id(context.bot.id).get("required_fields", {}).get("name", False)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_unit", update),
        reply_markup=cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )


async def edit_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"],
                           update.effective_user.id):
        context.user_data["edit"] = False
        await user(update, context)
        return

    context.user_data["state"] = State.EDIT_PLACE.name
    context.user_data["user_id"] = ObjectId(
        update.callback_query.data.split(" ")[1])

    is_required = BotsDb.get_bot_by_id(context.bot.id).get("required_fields", {}).get("name", False)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_place", update),
        reply_markup=cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )


async def edit_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"],
                           update.effective_user.id):
        context.user_data["edit"] = False
        await user(update, context)
        return

    context.user_data["state"] = State.EDIT_PHONE.name
    context.user_data["user_id"] = ObjectId(
        update.callback_query.data.split(" ")[1])

    is_required = BotsDb.get_bot_by_id(context.bot.id).get("required_fields", {}).get("name", False)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_phone", update),
        reply_markup=cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )


async def edit_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"],
                           update.effective_user.id):
        context.user_data["edit"] = False
        await user(update, context)
        return

    context.user_data["state"] = State.EDIT_EMAIL.name
    context.user_data["user_id"] = ObjectId(
        update.callback_query.data.split(" ")[1])

    is_required = BotsDb.get_bot_by_id(context.bot.id).get("required_fields", {}).get("name", False)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_email", update),
        reply_markup=cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )


async def user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"],
                           update.effective_user.id):
        context.user_data["edit"] = False
        await user(update, context)
        return

    user_id = ObjectId(update.callback_query.data.split(" ")[1])

    BotsDb.toggle_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], user_id)

    await user(update, context)


async def user_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"],
                           update.effective_user.id):
        context.user_data["edit"] = False
        await user(update, context)
        return

    user_id = ObjectId(update.callback_query.data.split(" ")[1])

    BotsDb.delete_user(BotsDb.get_bot_by_id(context.bot.id)["_id"], user_id)

    await contacts(update, context, delete=True)


async def user_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await delete_messages(update, context)

    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
        context.user_data["edit"] = False

    await contacts(update, context)


async def user_unmerge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"],
                           update.effective_user.id):
        context.user_data["edit"] = False
        await user(update, context)
        return

    bot_id = BotsDb.get_bot_by_id(context.bot.id)["_id"]

    user_id = ObjectId(update.callback_query.data.split(" ")[1])

    if not BotsDb.unmerge_user(bot_id, user_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("user_not_unmerged", update),
            parse_mode=PARSE_MODE,
        )

    await user(update, context, user_id)


async def user_merge(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"],
                           update.effective_user.id):
        context.user_data["edit"] = False
        await user(update, context)
        return

    bot_id = BotsDb.get_bot_by_id(context.bot.id)["_id"]

    user_id = ObjectId(update.callback_query.data.split(" ")[1])

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    users = BotsDb.get_users_to_merge(bot_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("user_merge", update),
        reply_markup=await keyboards.user_merge(user_id, context.bot, users, page, update),
        parse_mode=PARSE_MODE,
    )


async def user_merge_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await user_merge(update, context, int(update.callback_query.data.split(" ")[-1]))


async def users_merge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"],
                           update.effective_user.id):
        context.user_data["edit"] = False
        await user(update, context)
        return

    bot_id = BotsDb.get_bot_by_id(context.bot.id)["_id"]

    user_id = ObjectId(update.callback_query.data.split(" ")[1])
    merge_user_id = ObjectId(update.callback_query.data.split(" ")[2])

    if not BotsDb.merge_id_and_data_users(bot_id, merge_user_id, user_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("user_not_merged", update),
            parse_mode=PARSE_MODE,
        )

    await user(update, context, user_id)


async def user_merge_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await user(update, context, ObjectId(update.callback_query.data.split(" ")[1]))


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (context.user_data.get("state") == State.EDIT_CAPTION.name and
            update.message.text == Languages.btn("cancel", update)):
        context.user_data["state"] = State.FAQ.name
        await faq(update, context)
        return

    if (context.user_data.get("state") in [State.ADD_QUESTION.name, State.EDIT_QUESTION.name, State.ADD_ANSWER.name, State.EDIT_ANSWER.name] and
            update.message.text == Languages.btn("cancel", update)):
        context.user_data["question"] = None
        context.user_data["state"] = State.FAQ.name

        question_id = context.user_data.get("question_id")
        context.user_data["question_id"] = None
        await faq_ans(update, context, question_id=question_id)
        return

    if (context.user_data.get("state") in [State.NAME.name, State.JOB_TITLE.name, State.UNIT.name, State.PLACE.name, State.PHONE.name, State.EMAIL.name] and
            update.message.text == Languages.btn("cancel", update)):
        context.user_data["user"] = None
        context.user_data["search"] = None
        context.user_data["state"] = State.IDLE.name
        if BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
            context.user_data["state"] = State.CONTACTS.name
            await contacts(update, context)
        return

    if (context.user_data.get("state") in [State.EDIT_NAME.name, State.EDIT_JOB.name, State.EDIT_UNIT.name, State.EDIT_PLACE.name, State.EDIT_PHONE.name, State.EDIT_EMAIL.name] and
            update.message.text == Languages.btn("cancel", update)):
        context.user_data["search"] = None
        context.user_data["state"] = State.CONTACTS.name

        user_id = context.user_data.get("user_id")
        context.user_data["user_id"] = None
        await user(update, context, user_id=user_id)
        return

    bot_obj = BotsDb.get_bot_by_id(context.bot.id)

    if BotsDb.is_admin(BotsDb.get_bot_by_id(context.bot.id)["_id"], update.effective_user.id):
        if context.user_data["state"] in [State.ADD_QUESTION.name, State.EDIT_QUESTION.name]:
            question = update.message.text
            if question is None or question.strip() == "":
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Languages.msg("invalid_question", update),
                    parse_mode=PARSE_MODE,
                )
                await faq_add(update, context)
                return

            context.user_data["state"] = State(State[context.user_data["state"]].value + 1).name
            context.user_data["question"] = {
                "question": question,
                "answers": [],
            }
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("send_answer", update),
                reply_markup=cancel(update),
                parse_mode=PARSE_MODE,
            )
            return
        elif context.user_data["state"] in [State.ADD_ANSWER.name, State.EDIT_ANSWER.name]:
            question = context.user_data.get("question")
            if question is None:
                context.user_data["search"] = None
                await faq(update, context, delete=True)
                return

            if update.message.text == Languages.btn("stop_answer", update):
                answers = question.get("answers", [])
                if not answers:
                    context.user_data["question"] = None
                    context.user_data["search"] = None
                    await faq(update, context)
                    return
                if context.user_data["state"] == State.ADD_ANSWER.name:
                    BotsDb.add_question(bot_obj["_id"], question["question"], answers)
                    text = Languages.msg("question_added", update)
                else:
                    if context.user_data.get("question_id") is None:
                        await faq(update, context, delete=True)
                        return
                    BotsDb.edit_question(bot_obj["_id"], context.user_data["question_id"], question["question"], answers)
                    text = Languages.msg("question_edited", update)

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    parse_mode=PARSE_MODE,
                )

                await faq(update, context)
                return

            chat_id = update.effective_chat.id
            message_id = update.effective_message.message_id

            context.user_data["question"]["answers"].append({"chat_id": chat_id, "message_id": message_id})

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("send_next_answer", update),
                reply_markup=keyboards.stop_answer(update),
                parse_mode=PARSE_MODE,
            )

            return
        elif context.user_data["state"] == State.EDIT_CAPTION.name:
            caption = update.message.text
            if caption is None or caption.strip() == "":
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Languages.msg("invalid_caption", update),
                    parse_mode=PARSE_MODE,
                )
                await edit_caption(update, context)
                return

            if caption == Languages.btn("reset_caption", update):
                BotsDb.edit_caption(BotsDb.get_bot_by_id(context.bot.id)["_id"], "")
                await faq(update, context)
                return

            BotsDb.edit_caption(BotsDb.get_bot_by_id(context.bot.id)["_id"], caption)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("caption_edited", update),
                parse_mode=PARSE_MODE,
            )
            await faq(update, context)
            return
        elif context.user_data["state"] in [State.EDIT_NAME.name, State.EDIT_JOB.name, State.EDIT_UNIT.name, State.EDIT_PLACE.name, State.EDIT_PHONE.name, State.EDIT_EMAIL.name]:
            user_id = context.user_data.get("user_id")
            if user_id is None:
                await contacts(update, context)
                return
            fields = bot_obj.get("required_fields", {})
            if context.user_data["state"] == State.EDIT_NAME.name:
                if not fields.get("name", False) and update.message.text.strip() == Languages.btn("reset", update):
                    BotsDb.reset_field(bot_obj["_id"], user_id, "name")
                else:
                    BotsDb.edit_user(bot_obj["_id"], user_id, name=update.message.text)
            elif context.user_data["state"] == State.EDIT_JOB.name:
                if not fields.get("job_title", False) and update.message.text.strip() == Languages.btn("reset", update):
                    BotsDb.reset_field(bot_obj["_id"], user_id, "job_title")
                else:
                    BotsDb.edit_user(bot_obj["_id"], user_id, job_title=update.message.text)
            elif context.user_data["state"] == State.EDIT_UNIT.name:
                if not fields.get("unit", False) and update.message.text.strip() == Languages.btn("reset", update):
                    BotsDb.reset_field(bot_obj["_id"], user_id, "unit")
                else:
                    BotsDb.edit_user(bot_obj["_id"], user_id, unit=update.message.text)
            elif context.user_data["state"] == State.EDIT_PLACE.name:
                if not fields.get("place", False) and update.message.text.strip() == Languages.btn("reset", update):
                    BotsDb.reset_field(bot_obj["_id"], user_id, "place")
                else:
                    BotsDb.edit_user(bot_obj["_id"], user_id, place=update.message.text)
            elif context.user_data["state"] == State.EDIT_PHONE.name:
                if not fields.get("phone", False) and update.message.text.strip() == Languages.btn("reset", update):
                    BotsDb.reset_field(bot_obj["_id"], user_id, "phone")
                elif not check_phone(update.message.text):
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=Languages.msg("invalid_phone", update),
                        parse_mode=PARSE_MODE,
                    )
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=Languages.msg("send_phone", update),
                        reply_markup=keyboards.reset(update) if fields.get("phone", False) else cancel(update),
                    )
                    return
                else:
                    BotsDb.edit_user(bot_obj["_id"], user_id, phone=update.message.text)
            elif context.user_data["state"] == State.EDIT_EMAIL.name:
                if not fields.get("email", False) and update.message.text.strip() == Languages.btn("reset", update):
                    BotsDb.reset_field(bot_obj["_id"], user_id, "email")
                elif not await check_email(update.message.text):
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=Languages.msg("invalid_email", update),
                        parse_mode=PARSE_MODE,
                    )
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=Languages.msg("send_email", update),
                        reply_markup=keyboards.reset(update) if fields.get("email", False) else cancel(update),
                    )
                    return
                else:
                    BotsDb.edit_user(bot_obj["_id"], user_id, email=update.message.text)
            await user(update, context, user_id=user_id)
            return

    if context.user_data.get("state", None) in [State.NAME.name, State.JOB_TITLE.name, State.UNIT.name, State.PLACE.name, State.PHONE.name, State.EMAIL.name]:
        if update.message.text == Languages.btn("cancel", update):
            context.user_data["user"] = None
            if BotsDb.is_admin(bot_obj["_id"], update.effective_user.id):
                context.user_data["state"] = State.CONTACTS.name
                await contacts(update, context)
            elif BotsDb.is_user(bot_obj["_id"], update.effective_user.id):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Languages.msg("dont_understand", update),
                    parse_mode=PARSE_MODE,
                )
            return

        field = State[context.user_data["state"]].name.lower()
        if (update.message.text is None or update.message.text.strip() == "" or
                context.user_data.get("state", None) == State.PHONE.name and not check_phone(update.message.text) or
                context.user_data.get("state", None) == State.EMAIL.name and not await check_email(update.message.text)):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("invalid_" + field, update),
                parse_mode=PARSE_MODE,
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("send_" + field, update),
                reply_markup=cancel(update),
                parse_mode=PARSE_MODE,
            )
            return
        else:
            if context.user_data.get("user") is None:
                context.user_data["user"] = {}
            context.user_data["user"][field] = update.message.text
            start_search = False
            next_field: Optional[str] = None
            for fld in bot_obj.get("required_fields", {}):
                if fld == field:
                    start_search = True
                elif start_search and bot_obj["required_fields"][fld]:
                    next_field = fld
                    break
            if next_field is not None:
                context.user_data["state"] = State[next_field.upper()].name
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Languages.msg("send_" + next_field, update),
                    reply_markup=cancel(update),
                    parse_mode=PARSE_MODE,
                )
                return

            fields = {
                fld: context.user_data["user"].get(fld, "") for fld in bot_obj.get("required_fields", {})
            }
            for fld in fields:
                if fields[fld] == "" and bot_obj["required_fields"][fld]:
                    if BotsDb.is_admin(bot_obj["_id"], update.effective_user.id):
                        context.user_data["state"] = State.CONTACTS.name
                        await contacts(update, context)
                        return
                    elif await check_user(update, context):
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=Languages.msg("dont_understand", update),
                            parse_mode=PARSE_MODE,
                        )
                        return

            if BotsDb.is_admin(bot_obj["_id"], update.effective_user.id):
                user_id = BotsDb.add_user_with_data(bot_obj["_id"], **fields)
                await user(update, context, user_id=user_id)
                return
            elif BotsDb.is_user(bot_obj["_id"], update.effective_user.id):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Languages.msg("dont_understand", update),
                    parse_mode=PARSE_MODE,
                )
                return

            user_id = BotsDb.add_temp_user(bot_obj["_id"], update.effective_user.id, **fields)
            user_obj = BotsDb.get_user(bot_obj["_id"], user_id)

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("not_user_request", update),
                parse_mode=PARSE_MODE,
            )

            for admin in BotsDb.get_admin_ids(bot_obj["_id"]):
                await context.bot.send_message(
                    chat_id=admin,
                    text=Languages.msg("request_user", update).format(data=await user_info(user_obj, update, context.bot)),
                    reply_markup=keyboards.accept_deny(bot_obj, user_id),
                    parse_mode=PARSE_MODE,
                )

            return

    context.user_data["search"] = update.message.text if update.message.text else ""
    if context.user_data["state"] == State.FAQ.name:
        await faq(update, context)
    elif context.user_data["state"] == State.CONTACTS.name:
        await contacts(update, context)
    else:
        await faq(update, context)
