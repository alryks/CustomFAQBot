from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from bson import ObjectId

from config import BOT, PARSE_MODE

from . import keyboards
from keyboards import cancel

from db import BotsDb

from .state import State

from misc import create_faq, filter_faq, create_contacts, filter_contacts, user_info, check_phone, check_email

from lang import Languages


async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    if BotsDb.is_user(bot_obj["_id"], update.effective_user.id):
        return True

    required_fields = bot_obj.get("required_fields", {})
    first_field: Optional[str] = None
    for field in required_fields:
        if required_fields[field]:
            first_field = field
            break

    if first_field is None:
        user_id = BotsDb.add_temp_user(bot_obj["_id"], update.effective_user.id)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("not_user_request", update),
            parse_mode=PARSE_MODE,
        )

        username = update.effective_user.full_name + (f" @{update.effective_user.username}" if update.effective_user.username else "")
        data = Languages.msg("telegram", update).format(telegram=username)

        for admin in bot_obj["admins"]:
            await BOT.app.bot.send_message(
                chat_id=admin,
                text=Languages.msg("request_user", update).format(
                    bot_name=context.bot.bot.username, data=data),
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
        text=Languages.msg("not_admin_request", update),
        parse_mode=PARSE_MODE,
    )

    name = update.effective_user.full_name + (f" @{update.effective_user.username}" if update.effective_user.username else "")
    bot_obj = BotsDb.get_bot_by_id(context.bot.id)

    for admin in bot_obj["admins"]:
        await BOT.app.bot.send_message(
            chat_id=admin,
            text=Languages.msg("request_admin", update).format(name=name, bot_name=context.bot.bot.username),
            reply_markup=keyboards.accept_deny(bot_obj, update.effective_user.id, is_admin=True),
            parse_mode=PARSE_MODE,
        )

    return False


async def run_faq(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False, delete=False, page=1) -> None:
    context.user_data["state"] = State.FAQ.name

    if not await check_user(update, context):
        return

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
        reply_markup=keyboards.faq(bot_faq, update, edit, page),
        parse_mode=PARSE_MODE,
    )


async def edit_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update, context):
        return
    await run_faq(update, context, edit=True)


async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search"] = None
    await run_faq(update, context)


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
    context.user_data["search"] = None
    await edit_faq(update, context)


async def run_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE, delete: bool = False, page: int = 1) -> None:
    context.user_data["state"] = State.CONTACTS.name

    if not await check_user(update, context):
        return

    search = context.user_data.get("search")
    if search is None:
        search = ""

    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    bot_faq = filter_contacts(bot_obj["users"], search)

    text = create_contacts(bot_faq, update, page)

    if delete:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboards.contacts(bot_faq, update, page),
        parse_mode=PARSE_MODE,
    )


async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search"] = None
    await run_contacts(update, context)


async def contacts_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_contacts(update, context, delete=True, page=int(update.callback_query.data.split(" ")[1]))


async def user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context):
        return

    user_id = ObjectId(update.callback_query.data.split(" ")[1])
    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    user_obj = BotsDb.get_user(bot_obj["_id"], user_id)

    text = await user_info(user_obj, update, context.bot)

    delete_message_ids = context.user_data.get("delete_message_ids")
    if delete_message_ids is not None:
        for delete_message_id in delete_message_ids:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=delete_message_id
            )

    context.user_data["delete_message_ids"] = []
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=PARSE_MODE,
    )
    context.user_data["delete_message_ids"].append(message.message_id)
    await update.callback_query.answer(
        text=Languages.msg("answer_sent", update),
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (context.user_data.get("state") in [State.EDIT_CAPTION,
                                           State.ADD_QUESTION.name,
                                           State.EDIT_QUESTION.name,
                                           State.ADD_ANSWER.name,
                                           State.EDIT_ANSWER.name] and
            update.message.text == Languages.btn("cancel", update)):
        context.user_data["question"] = None
        context.user_data["answers"] = None
        context.user_data["search"] = None
        context.user_data["state"] = State.IDLE.name
        await edit_faq(update, context)
        return

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
            context.user_data["question"] = question.strip()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("send_answer", update),
                reply_markup=keyboards.stop_answer(update),
                parse_mode=PARSE_MODE,
            )
            context.user_data["answers"] = None
            return
        elif context.user_data["state"] in [State.ADD_ANSWER.name, State.EDIT_ANSWER.name]:
            question = context.user_data.get("question")
            if question is None:
                context.user_data["search"] = None
                await run_faq(update, context, edit=True, delete=True)
                return

            if update.message.text == Languages.btn("stop_answer", update):
                answers = context.user_data.get("answers")
                if answers is None:
                    context.user_data["question"] = None
                    context.user_data["answers"] = None
                    context.user_data["search"] = None
                    await edit_faq(update, context)
                    return
                bot_obj = BotsDb.get_bot_by_id(context.bot.id)
                if context.user_data["state"] == State.ADD_ANSWER.name:
                    BotsDb.add_question(bot_obj["_id"], question, answers)
                    text = Languages.msg("question_added", update)
                else:
                    if context.user_data.get("question_id") is None:
                        await run_faq(update, context, edit=True, delete=True)
                        return
                    BotsDb.edit_question(bot_obj["_id"], context.user_data["question_id"], question, answers)
                    text = Languages.msg("question_edited", update)

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    parse_mode=PARSE_MODE,
                )

                await edit_faq(update, context)
                return

            chat_id = update.effective_chat.id
            message_id = update.effective_message.message_id

            if context.user_data.get("answers") is None:
                context.user_data["answers"] = []

            context.user_data["answers"].append({"chat_id": chat_id, "message_id": message_id})

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
                await edit_faq(update, context)
                return

            BotsDb.edit_caption(BotsDb.get_bot_by_id(context.bot.id)["_id"], caption)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("caption_edited", update),
                parse_mode=PARSE_MODE,
            )
            await edit_faq(update, context)
            return

    bot_obj = BotsDb.get_bot_by_id(context.bot.id)

    if not BotsDb.is_user(bot_obj["_id"], update.effective_user.id):
        if context.user_data.get("state", None) in [State.NAME.name, State.JOB_TITLE.name, State.UNIT.name, State.PLACE.name, State.PHONE.name, State.EMAIL.name]:
            if update.message.text == Languages.btn("cancel", update):
                context.user_data["state"] = State.IDLE.name
                return
            field = State[context.user_data["state"]].name.lower()
            if update.message.text is None or update.message.text.strip() == "":
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
            else:
                if (context.user_data.get("state", None) == State.PHONE.name and not check_phone(update.message.text) or
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
                context.user_data[field] = update.message.text
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
                    fld: context.user_data.get(fld, "") for fld in bot_obj.get("required_fields", {})
                }
                data = ""
                for fld in fields:
                    if fields[fld] == "" and bot_obj["required_fields"][fld]:
                        await start(update, context)
                        return
                    elif fields[fld] != "":
                        data += Languages.msg(fld, update).format(**{fld: fields[fld]}) + "\n"
                username = update.effective_user.full_name + (f" @{update.effective_user.username}" if update.effective_user.username else "")
                data += Languages.msg("telegram", update).format(telegram=username)

                user_id = BotsDb.add_temp_user(bot_obj["_id"], update.effective_user.id, **fields)

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Languages.msg("not_user_request", update),
                    parse_mode=PARSE_MODE,
                )

                for admin in bot_obj["admins"]:
                    await BOT.app.bot.send_message(
                        chat_id=admin,
                        text=Languages.msg("request_user", update).format(bot_name=context.bot.bot.username, data=data),
                        reply_markup=keyboards.accept_deny(bot_obj, user_id),
                        parse_mode=PARSE_MODE,
                    )

        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("dont_understand", update),
                parse_mode=PARSE_MODE,
            )
        return

    context.user_data["search"] = update.message.text if update.message.text else ""
    if context.user_data["state"] == State.FAQ.name:
        await run_faq(update, context)
    elif context.user_data["state"] == State.CONTACTS.name:
        await run_contacts(update, context)
    else:
        await edit_faq(update, context)


async def faq_ans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user(update, context):
        return

    question = BotsDb.get_question(BotsDb.get_bot_by_id(context.bot.id)["_id"], ObjectId(update.callback_query.data.split(" ")[1]))
    if question is None:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id,
        )
        await run_faq(update, context)
        return
    answers = question["answers"]

    delete_message_ids = context.user_data.get("delete_message_ids")
    if delete_message_ids is not None:
        for delete_message_id in delete_message_ids:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=delete_message_id
            )

    context.user_data["delete_message_ids"] = []
    for answer in answers:
        message = await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=answer["chat_id"],
            message_id=answer["message_id"],
        )
        context.user_data["delete_message_ids"].append(message.message_id)
    await update.callback_query.answer(
        text=Languages.msg("answer_sent", update),
    )


async def faq_ans_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_faq(update, context, delete=True, page=int(update.callback_query.data.split(" ")[1]))


async def edit_caption(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update, context):
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


async def faq_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update, context):
        return

    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    question = BotsDb.get_question(bot_obj["_id"], ObjectId(update.callback_query.data.split(" ")[1]))
    if question is None:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await edit_faq(update, context)
        return

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("current_question", update).format(question=question["question"]),
        parse_mode=PARSE_MODE,
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("current_answers", update),
        parse_mode=PARSE_MODE,
    )

    for answer in question["answers"]:
        await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=answer["chat_id"],
            message_id=answer["message_id"],
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("question_action", update),
        reply_markup=keyboards.faq_edit(question["_id"], update),
        parse_mode=PARSE_MODE,
    )


async def faq_edit_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_faq(update, context, edit=True, delete=True, page=int(update.callback_query.data.split(" ")[1]))


async def faq_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update, context):
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


async def faq_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )


async def question_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update, context):
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
    if not await check_admin(update, context):
        return

    question_id = ObjectId(update.callback_query.data.split(" ")[1])
    bot_obj = BotsDb.get_bot_by_id(context.bot.id)
    BotsDb.delete_question(bot_obj["_id"], question_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("question_deleted", update),
        parse_mode=PARSE_MODE,
    )

    await run_faq(update, context, edit=True, delete=True)


async def question_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update, context):
        return

    await run_faq(update, context, edit=True, delete=True)