from telegram import Update
from telegram.ext import ContextTypes, Application

from bson import ObjectId

from typing import Optional

from config import PARSE_MODE

import keyboards

from db import BotsDb

from state import State, bots

from CustomBot.custom_bot import CustomBot

from lang import Languages

from misc import user_info, check_phone, check_email

from verify_email import verify_email
import phonenumbers


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, page=1) -> None:
    context.user_data["state"] = State.IDLE.name

    bot_usernames = await BotsDb.get_user_bot_usernames(update.effective_user.id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("your_faqs", update) if bot_usernames else Languages.msg("no_faqs", update),
        reply_markup=keyboards.bots(bot_usernames, page, update),
        parse_mode=PARSE_MODE,
    )


async def bot_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query is not None:
        if update.callback_query.data == "bots_add":
            context.user_data["state"] = State.ADD_TOKEN.name
        else:
            context.user_data["state"] = State.EDIT_TOKEN.name
            context.user_data["bot_id"] = ObjectId(update.callback_query.data.split(" ")[1])

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_token", update),
        reply_markup=keyboards.cancel(update),
        parse_mode=PARSE_MODE,
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (context.user_data.get("state") not in [State.ADD_TOKEN.name, State.EDIT_TOKEN.name,
                                               State.ADD_USER.name, State.EDIT_NAME.name, State.EDIT_JOB.name, State.EDIT_UNIT.name, State.EDIT_PLACE.name, State.EDIT_PHONE.name, State.EDIT_EMAIL.name] or
            update.message.text is None or update.message.text.strip() == ""):
        await update.message.reply_text(Languages.msg("dont_understand", update))
        return
    if update.message.text == Languages.btn("cancel", update):
        if context.user_data["state"] == State.ADD_TOKEN.name:
            await start(update, context)
        elif context.user_data["state"] == State.EDIT_TOKEN.name:
            context.user_data["state"] = State.IDLE.name
            await bot(update, context)
        elif context.user_data["state"] == State.ADD_USER.name:
            data = await context_data_check_bot(update, context)
            if data is None:
                return
            await bot_users(update, context)
        elif context.user_data["state"] in [State.EDIT_NAME.name, State.EDIT_JOB.name, State.EDIT_UNIT.name, State.EDIT_PLACE.name, State.EDIT_PHONE.name, State.EDIT_EMAIL.name]:
            data = await context_data_check_bot(update, context)
            if data is None:
                return
            await user(update, context, ObjectId(context.user_data.get("user_id", "")))
        return

    if context.user_data["state"] == State.EDIT_TOKEN.name:
        data = await context_data_check_bot(update, context)
        if data is None:
            return

    if context.user_data["state"] == State.ADD_USER.name:
        bot_id = context.user_data.get("bot_id")
        if bot_id is None:
            await start(update, context)
            return
        user_id = BotsDb.add_user_with_data(bot_id, update.message.text)
        await user(update, context, user_id)
        return

    if context.user_data["state"] in [State.EDIT_NAME.name, State.EDIT_JOB.name, State.EDIT_UNIT.name, State.EDIT_PLACE.name, State.EDIT_PHONE.name, State.EDIT_EMAIL.name]:
        bot_id = context.user_data.get("bot_id")
        if bot_id is None:
            await start(update, context)
            return
        user_id = context.user_data.get("user_id")
        if user_id is None:
            await bot_users(update, context)
            return
        fields = BotsDb.get_bot(bot_id).get("required_fields", {})
        if context.user_data["state"] == State.EDIT_NAME.name:
            if not fields.get("name", False) and update.message.text.strip() == Languages.btn("reset", update):
                BotsDb.reset_field(bot_id, user_id, "name")
            else:
                BotsDb.edit_user(bot_id, user_id, name=update.message.text)
        elif context.user_data["state"] == State.EDIT_JOB.name:
            if not fields.get("job_title", False) and update.message.text.strip() == Languages.btn("reset", update):
                BotsDb.reset_field(bot_id, user_id, "job_title")
            else:
                BotsDb.edit_user(bot_id, user_id, job_title=update.message.text)
        elif context.user_data["state"] == State.EDIT_UNIT.name:
            if not fields.get("unit", False) and update.message.text.strip() == Languages.btn("reset", update):
                BotsDb.reset_field(bot_id, user_id, "unit")
            else:
                BotsDb.edit_user(bot_id, user_id, unit=update.message.text)
        elif context.user_data["state"] == State.EDIT_PLACE.name:
            if not fields.get("place", False) and update.message.text.strip() == Languages.btn("reset", update):
                BotsDb.reset_field(bot_id, user_id, "place")
            else:
                BotsDb.edit_user(bot_id, user_id, place=update.message.text)
        elif context.user_data["state"] == State.EDIT_PHONE.name:
            if not fields.get("phone", False) and update.message.text.strip() == Languages.btn("reset", update):
                BotsDb.reset_field(bot_id, user_id, "phone")
            elif not check_phone(update.message.text):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Languages.msg("invalid_phone", update),
                    parse_mode=PARSE_MODE,
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Languages.msg("send_phone", update),
                    reply_markup=keyboards.reset(update),
                )
                return
            else:
                BotsDb.edit_user(bot_id, user_id, phone=update.message.text)
        elif context.user_data["state"] == State.EDIT_EMAIL.name:
            if not fields.get("email", False) and update.message.text.strip() == Languages.btn("reset", update):
                BotsDb.reset_field(bot_id, user_id, "email")
            elif not await check_email(update.message.text):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Languages.msg("invalid_email", update),
                    parse_mode=PARSE_MODE,
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Languages.msg("send_email", update),
                    reply_markup=keyboards.reset(update),
                )
                return
            else:
                BotsDb.edit_user(bot_id, user_id, email=update.message.text)
        context.user_data["state"] = State.IDLE.name
        await user(update, context, user_id, delete=False)
        return

    user_bot = CustomBot(update.message.text)
    if not await user_bot.run():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("invalid_token", update),
            parse_mode=PARSE_MODE,
        )
        await bot_token(update, context)
        return

    if context.user_data["state"] == State.EDIT_TOKEN.name:
        bot_id = context.user_data.get("bot_id")
        if bot_id is None:
            await user_bot.stop()
            await start(update, context)
            return

        bot_obj = BotsDb.get_bot(bot_id)
        if bot_obj is None:
            await user_bot.stop()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("bot_not_found", update),
                parse_mode=PARSE_MODE,
            )
            await start(update, context)
            return

        if bot_obj["bot_id"] != user_bot.app.bot.id:
            await user_bot.stop()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("token_doesnt_match", update),
                parse_mode=PARSE_MODE,
            )
            await bot_token(update, context)
            return

        BotsDb.edit_token(bot_id, update.message.text)
        if bot_id in bots:
            await bots[bot_id].stop()
            bots.pop(bot_id)
    else:
        bot_id = BotsDb.add_bot(user_bot.app.bot.id, update.message.text, update.effective_user.id)
        if bot_id is None:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Languages.msg("bot_exists", update),
                parse_mode=PARSE_MODE,
            )
            await bot_token(update, context)
            return
        context.user_data["bot_id"] = bot_id

    bots[bot_id] = user_bot
    context.user_data["state"] = State.IDLE.name
    await bot(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )


async def bot_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await start(update, context, int(update.callback_query.data.split(" ")[1]))


async def callback_check_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[tuple[ObjectId, Application]]:
    bot_id = ObjectId(update.callback_query.data.split(" ")[1])
    if not BotsDb.is_admin(bot_id, update.effective_user.id):
        await update.callback_query.answer(Languages.msg("not_admin", update))
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    if bot_id not in bots:
        await update.callback_query.answer(Languages.msg("bot_not_found", update))
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    app = bots[bot_id].app
    if app is None:
        bots.pop(bot_id)
        await update.callback_query.answer(Languages.msg("bot_not_found", update))
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    return bot_id, app


async def context_data_check_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[tuple[ObjectId, Application]]:
    bot_id = context.user_data.get("bot_id")
    if bot_id is None:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    if not BotsDb.is_admin(bot_id, update.effective_user.id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("not_admin", update),
            parse_mode=PARSE_MODE,
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    if bot_id not in bots:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("bot_not_found", update),
            parse_mode=PARSE_MODE,
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    app = bots[bot_id].app
    if app is None:
        bots.pop(bot_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("bot_not_found", update),
            parse_mode=PARSE_MODE,
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        await start(update, context)
        return

    return bot_id, app


async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    user_id = ObjectId(update.callback_query.data.split(" ")[2])

    if BotsDb.is_temp_user(bot_id, user_id):
        BotsDb.set_perm_user(bot_id, user_id)
        tg_id = BotsDb.get_user(bot_id, user_id).get("tg_id", 0)
        await app.bot.send_message(
            chat_id=tg_id,
            text=Languages.msg("user_accepted", update).format(bot_name=app.bot.bot.username),
            parse_mode=PARSE_MODE,
        )

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )


async def deny(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    user_id = ObjectId(update.callback_query.data.split(" ")[2])

    if BotsDb.is_temp_user(bot_id, user_id):
        tg_id = BotsDb.get_user(bot_id, user_id).get("tg_id", 0)
        await app.bot.send_message(
            chat_id=tg_id,
            text=Languages.msg("user_denied", update).format(bot_name=app.bot.bot.username),
            parse_mode=PARSE_MODE,
        )
        BotsDb.delete_temp_user(bot_id, user_id)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )


async def bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    if update.callback_query is not None:
        data = await callback_check_bot(update, context)
    else:
        data = await context_data_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    bot_username = app.bot.bot.username

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("your_bot", update).format(bot_username=bot_username),
        reply_markup=keyboards.bot(BotsDb.get_bot(bot_id), update),
        parse_mode=PARSE_MODE,
    )


async def bot_private(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    BotsDb.toggle_private(bot_id)

    await bot(update, context)


async def bot_users(update: Update, context: ContextTypes.DEFAULT_TYPE, page=1) -> None:
    if update.callback_query is not None:
        data = await callback_check_bot(update, context)
    else:
        data = await context_data_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    username = app.bot.bot.username

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("users", update).format(bot_username=username),
        reply_markup=await keyboards.users(BotsDb.get_bot(bot_id), app.bot, page, update),
        parse_mode=PARSE_MODE,
    )


async def users_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot_users(update, context, int(update.callback_query.data.split(" ")[2]))


async def bot_required(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("required", update),
        reply_markup=keyboards.required(BotsDb.get_bot(bot_id), update),
        parse_mode=PARSE_MODE,
    )


async def required_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    field = "_".join(update.callback_query.data.split(" ")[0].split("_")[1:])

    if field == "name":
        await update.callback_query.answer(Languages.msg("name_is_required", update))
        return

    BotsDb.toggle_required(bot_id, field)

    await bot_required(update, context)


async def required_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot(update, context)


async def bot_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data
    BotsDb.delete_bot(bot_id)
    if bot_id in bots:
        await bots[bot_id].stop()
        bots.pop(bot_id)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    await start(update, context)


async def bot_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    await start(update, context)


async def user_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    user_id = ObjectId(update.callback_query.data.split(" ")[2])

    BotsDb.delete_user(bot_id, user_id)

    await bot_users(update, context)


async def users_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    context.user_data["state"] = State.ADD_USER.name
    context.user_data["bot_id"] = bot_id

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_name", update),
        reply_markup=keyboards.cancel(update),
        parse_mode=PARSE_MODE,
    )


async def users_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot(update, context)


async def user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: ObjectId = None, delete=True) -> None:
    if update.callback_query is not None:
        data = await callback_check_bot(update, context)
        user_id = ObjectId(update.callback_query.data.split(" ")[2])
    else:
        data = await context_data_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    user_obj = BotsDb.get_user(bot_id, user_id)
    if user_obj is None:
        await bot_users(update, context)
        return

    if delete:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )

    is_merge = True if user_obj.get("tg_id", 0) == 0 else False

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=await user_info(user_obj, update, app.bot),
        reply_markup=keyboards.user(bot_id, user_obj, user_obj["tg_id"] != update.effective_user.id, update, is_merge),
        parse_mode=PARSE_MODE,
    )


async def user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    user_id = ObjectId(update.callback_query.data.split(" ")[2])

    BotsDb.toggle_admin(bot_id, user_id)

    await user(update, context, user_id)


async def user_unmerge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    user_id = ObjectId(update.callback_query.data.split(" ")[2])

    if not BotsDb.unmerge_user(bot_id, user_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("user_not_unmerged", update),
            parse_mode=PARSE_MODE,
        )

    await user(update, context, user_id)


async def user_merge(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1) -> None:
    data = await callback_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    user_id = ObjectId(update.callback_query.data.split(" ")[2])

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    context.user_data["user_id"] = user_id
    users = BotsDb.get_users_to_merge(bot_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("user_merge", update),
        reply_markup=await keyboards.user_merge(bot_id, user_id, app.bot, users, page, update),
        parse_mode=PARSE_MODE,
    )


async def user_merge_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await user_merge(update, context, int(update.callback_query.data.split(" ")[-1]))


async def users_merge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    user_id = context.user_data.get("user_id", ObjectId())
    merge_user_id = ObjectId(update.callback_query.data.split(" ")[2])

    if not BotsDb.merge_id_and_data_users(bot_id, merge_user_id, user_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Languages.msg("user_not_merged", update),
            parse_mode=PARSE_MODE,
        )

    await user(update, context, user_id)


async def user_merge_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await user(update, context, ObjectId(update.callback_query.data.split(" ")[2]))


async def edit_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query is not None:
        data = await callback_check_bot(update, context)
        user_id = ObjectId(update.callback_query.data.split(" ")[2])
    else:
        data = await context_data_check_bot(update, context)
        user_id = context.user_data.get("user_id")
    if data is None:
        return
    bot_id, app = data

    context.user_data["state"] = State.EDIT_NAME.name
    context.user_data["bot_id"] = bot_id
    context.user_data["user_id"] = user_id

    is_required = BotsDb.get_bot(bot_id).get("required_fields", {}).get("name", False)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_name", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )


async def edit_job_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query is not None:
        data = await callback_check_bot(update, context)
        user_id = ObjectId(update.callback_query.data.split(" ")[2])
    else:
        data = await context_data_check_bot(update, context)
        user_id = context.user_data.get("user_id")
    if data is None:
        return
    bot_id, app = data

    context.user_data["state"] = State.EDIT_JOB.name
    context.user_data["bot_id"] = bot_id
    context.user_data["user_id"] = user_id

    is_required = BotsDb.get_bot(bot_id).get("required_fields", {}).get("job_title", False)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_job_title", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )


async def edit_unit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query is not None:
        data = await callback_check_bot(update, context)
        user_id = ObjectId(update.callback_query.data.split(" ")[2])
    else:
        data = await context_data_check_bot(update, context)
        user_id = context.user_data.get("user_id")
    if data is None:
        return
    bot_id, app = data

    context.user_data["state"] = State.EDIT_UNIT.name
    context.user_data["bot_id"] = bot_id
    context.user_data["user_id"] = user_id

    is_required = BotsDb.get_bot(bot_id).get("required_fields", {}).get("unit", False)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_unit", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )


async def edit_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query is not None:
        data = await callback_check_bot(update, context)
        user_id = ObjectId(update.callback_query.data.split(" ")[2])
    else:
        data = await context_data_check_bot(update, context)
        user_id = context.user_data.get("user_id")
    if data is None:
        return
    bot_id, app = data

    context.user_data["state"] = State.EDIT_PLACE.name
    context.user_data["bot_id"] = bot_id
    context.user_data["user_id"] = user_id

    is_required = BotsDb.get_bot(bot_id).get("required_fields", {}).get("place", False)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_place", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )


async def edit_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query is not None:
        data = await callback_check_bot(update, context)
        user_id = ObjectId(update.callback_query.data.split(" ")[2])
    else:
        data = await context_data_check_bot(update, context)
        user_id = context.user_data.get("user_id")
    if data is None:
        return
    bot_id, app = data

    context.user_data["state"] = State.EDIT_PHONE.name
    context.user_data["bot_id"] = bot_id
    context.user_data["user_id"] = user_id

    is_required = BotsDb.get_bot(bot_id).get("required_fields", {}).get("phone", False)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_phone", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )


async def edit_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query is not None:
        data = await callback_check_bot(update, context)
        user_id = ObjectId(update.callback_query.data.split(" ")[2])
    else:
        data = await context_data_check_bot(update, context)
        user_id = context.user_data.get("user_id")
    if data is None:
        return
    bot_id, app = data

    context.user_data["state"] = State.EDIT_EMAIL.name
    context.user_data["bot_id"] = bot_id
    context.user_data["user_id"] = user_id

    is_required = BotsDb.get_bot(bot_id).get("required_fields", {}).get("email", False)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Languages.msg("send_email", update),
        reply_markup=keyboards.cancel(update) if is_required else keyboards.reset(update),
        parse_mode=PARSE_MODE,
    )


async def user_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot_users(update, context)
