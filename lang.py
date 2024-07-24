from telegram import Update


class Languages:
    langs = [
        "en",
        "ru"
    ]

    _msg = {
        "dont_understand": {
            "en": "I don't understand you!",
            "ru": "Я вас не понимаю!"
        },
        "your_faqs": {
            "en": "Your FAQs:",
            "ru": "Ваши ЧаВо:"
        },
        "no_faqs": {
            "en": "You have no FAQs!",
            "ru": "У вас нет ЧаВо!"
        },
        "your_bot": {
            "en": "Your @{bot_username}:",
            "ru": "Ваш @{bot_username}:"
        },
        "users": {
            "en": "@{bot_username} users:",
            "ru": "Пользователи @{bot_username}:"
        },
        "admins": {
            "en": "@{bot_username} admins:",
            "ru": "Администраторы @{bot_username}:"
        },
        "send_token": {
            "en": "Send token of your bot:",
            "ru": "Отправьте токен вашего бота:"
        },
        "invalid_token": {
            "en": "Invalid token!",
            "ru": "Некорректный токен!"
        },
        "bot_not_found": {
            "en": "Bot not found!",
            "ru": "Бот не найден!"
        },
        "token_doesnt_match": {
            "en": "Token doesn't match the bot!",
            "ru": "Токен не соответствует боту!"
        },
        "bot_exists": {
            "en": "Bot already exists!",
            "ru": "Бот уже существует!"
        },
        "not_admin": {
            "en": "You are not bot admin!",
            "ru": "Вы не являетесь администратором бота!"
        },
        "not_user_request": {
            "en": "You are not bot user! Requesting access...",
            "ru": "Вы не являетесь пользователем бота! Запрашиваю доступ..."
        },
        "not_admin_request": {
            "en": "You are not bot admin! Requesting access...",
            "ru": "Вы не являетесь администратором бота! Запрашиваю доступ..."
        },
        "request_user": {
            "en": "User <b>{name}</b> requested access to @{bot_name}",
            "ru": "Пользователь <b>{name}</b> запросил доступ к @{bot_name}"
        },
        "request_admin": {
            "en": "User <b>{name}</b> requested <b>admin rights</b> to @{bot_name}",
            "ru": "Пользователь <b>{name}</b> запросил <b>права администратора</b> к @{bot_name}"
        },
        "faq": {
            "en": "FAQ for @{bot_username}:",
            "ru": "ЧаВо для @{bot_username}:"
        },
        "no_faq": {
            "en": "FAQ for @{bot_username} is empty!",
            "ru": "ЧаВо для @{bot_username} пусто!"
        },
        "send_caption": {
            "en": "Send caption for @{bot_username}:",
            "ru": "Отправьте описание для @{bot_username}:"
        },
        "invalid_caption": {
            "en": "Invalid caption!",
            "ru": "Некорректное описание!"
        },
        "caption_edited": {
            "en": "Caption edited!",
            "ru": "Описание изменено!"
        },
        "send_question": {
            "en": "Send question:",
            "ru": "Отправьте вопрос:"
        },
        "send_new_question": {
            "en": "Send new question:",
            "ru": "Отправьте новый вопрос:"
        },
        "invalid_question": {
            "en": "Invalid question!",
            "ru": "Некорректный вопрос!"
        },
        "send_answer": {
            "en": "Send answer:",
            "ru": "Отправьте ответ:"
        },
        "send_next_answer": {
            "en": "Send next answer:",
            "ru": "Отправьте следующий ответ:"
        },
        "answer_sent": {
            "en": "Answer sent!",
            "ru": "Ответ отправлен!"
        },
        "current_question": {
            "en": "<i>Current question:</i>\n\n{question}",
            "ru": "<i>Текущий вопрос:</i>\n\n{question}"
        },
        "current_answers": {
            "en": "<i>Current answers:</i>",
            "ru": "<i>Текущие ответы:</i>"
        },
        "question_action": {
            "en": "What do you want to do with this question?",
            "ru": "Что вы хотите сделать с этим вопросом?"
        },
        "question_added": {
            "en": "Question added!",
            "ru": "Вопрос добавлен!"
        },
        "question_edited": {
            "en": "Question edited!",
            "ru": "Вопрос изменен!"
        },
        "question_deleted": {
            "en": "Question deleted!",
            "ru": "Вопрос удален!"
        },
    }

    _btn = {
        "cancel": {
            "en": "✖️Cancel",
            "ru": "✖️Отмена"
        },
        "stop_answer": {
            "en": "🛑Stop answering",
            "ru": "🛑Завершить ввод"
        },
        "reset_caption": {
            "en": "🔄Reset Caption",
            "ru": "🔄Сбросить описание"
        },
    }

    _kbd = {
        "cancel": {
            "en": "✖️Cancel",
            "ru": "✖️Отмена"
        },
        "add": {
            "en": "➕Add",
            "ru": "➕Добавить"
        },
        "add_question": {
            "en": "➕Add Question",
            "ru": "➕Добавить вопрос"
        },
        "edit": {
            "en": "✏️Edit",
            "ru": "✏️Изменить"
        },
        "edit_token": {
            "en": "🔑Edit Token",
            "ru": "🔑Изменить токен"
        },
        "edit_caption": {
            "en": "📝Edit Caption",
            "ru": "📝Изменить описание"
        },
        "private": {
            "en": "🔒Private: {private}",
            "ru": "🔒Приватный: {private}"
        },
        "users": {
            "en": "👥Users",
            "ru": "👥Пользователи"
        },
        "admins": {
            "en": "🚨Admins",
            "ru": "🚨Администраторы"
        },
        "delete": {
            "en": "❌Delete",
            "ru": "❌Удалить"
        },
        "back": {
            "en": "🔙Back",
            "ru": "🔙Назад"
        },
    }

    @classmethod
    def get(cls, field: str, key: str, update: Update) -> str:
        lang = update.effective_user.language_code
        text_langs: dict = cls.__dict__[field].get(key)
        if text_langs is None:
            return ""

        if lang in text_langs:
            return text_langs.get(lang)

        return sorted(text_langs.items(), key=lambda x: cls.langs.index(x[0]))[0][1]

    @classmethod
    def msg(cls, key: str, update: Update) -> str:
        return cls.get("_msg", key, update)

    @classmethod
    def btn(cls, key: str, update: Update) -> str:
        return cls.get("_btn", key, update)

    @classmethod
    def kbd(cls, key: str, update: Update) -> str:
        return cls.get("_kbd", key, update)