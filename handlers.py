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
    if (context.user_data.get("state") not in [State.ADD_TOKEN.name, State.EDIT_TOKEN.name] or
            update.message.text is None):
        await update.message.reply_text(Languages.msg("dont_understand", update))
        return
    if update.message.text == Languages.btn("cancel", update):
        if context.user_data["state"] == State.ADD_TOKEN.name:
            await start(update, context)
        else:
            context.user_data["state"] = State.IDLE.name
            await bot(update, context)
        return

    if context.user_data["state"] == State.EDIT_TOKEN.name:
        data = await context_data_check_bot(update, context)
        if data is None:
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

    user_id = int(update.callback_query.data.split(" ")[2])
    access_type = update.callback_query.data.split(" ")[0].split("_")[1]

    if access_type == "admin":
        BotsDb.add_admin(bot_id, user_id)
    else:
        BotsDb.add_user_with_id(bot_id, user_id)

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


async def bot_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
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
        reply_markup=await keyboards.users(BotsDb.get_bot(bot_id), app.bot, update),
        parse_mode=PARSE_MODE,
    )


async def bot_admins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
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
        text=Languages.msg("admins", update).format(bot_username=username),
        reply_markup=await keyboards.admins(BotsDb.get_bot(bot_id), update.effective_user.id, app.bot, update),
        parse_mode=PARSE_MODE,
    )


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


async def users_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot(update, context)


async def admin_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await callback_check_bot(update, context)
    if data is None:
        return
    bot_id, app = data

    admin_id = int(update.callback_query.data.split(" ")[2])

    BotsDb.delete_admin(bot_id, admin_id)

    await bot_admins(update, context)


async def admins_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot(update, context)
