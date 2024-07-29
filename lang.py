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
        "empty": {
            "en": "Empty...",
            "ru": "Пусто..."
        },
        "start": {
            "en": "Welcome! I'm your company navigator. I can help you find the right employee and answer questions.",
            "ru": "Приветствую! Я твой навигатор по компании. Я могу помочь тебе найти нужного сотрудника, а также ответить на вопросы."
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
        "users": {
            "en": "@{bot_username} users:",
            "ru": "Пользователи @{bot_username}:"
        },
        "general_info": {
            "en": "<b>General info:</b>",
            "ru": "<b>Общая информация:</b>"
        },
        "contacts": {
            "en": "<b>Contacts:</b>",
            "ru": "<b>Контакты:</b>"
        },
        "name": {
            "en": "<i>Name:</i> {name}",
            "ru": "<i>Имя:</i> {name}"
        },
        "job_title": {
            "en": "<i>Job Title:</i> {job_title}",
            "ru": "<i>Должность:</i> {job_title}"
        },
        "unit": {
            "en": "<i>Unit:</i> {unit}",
            "ru": "<i>Подразделение:</i> {unit}"
        },
        "place": {
            "en": "<i>Place of work:</i> {place}",
            "ru": "<i>Место работы:</i> {place}"
        },
        "phone": {
            "en": "<i>Phone:</i> {phone}",
            "ru": "<i>Телефон:</i> {phone}"
        },
        "email": {
            "en": "<i>Email:</i> {email}",
            "ru": "<i>Почта:</i> {email}"
        },
        "telegram": {
            "en": "<i>Telegram:</i> {telegram}",
            "ru": "<i>Телеграм:</i> {telegram}"
        },
        "send_name": {
            "en": "Send full name:",
            "ru": "Отправьте ФИО:"
        },
        "invalid_name": {
            "en": "Invalid user name!",
            "ru": "Некорректное имя пользователя!"
        },
        "send_job_title": {
            "en": "Send job title:",
            "ru": "Отправьте должность:"
        },
        "invalid_job_title": {
            "en": "Invalid job title!",
            "ru": "Некорректная должность!"
        },
        "send_unit": {
            "en": "Send unit:",
            "ru": "Отправьте подразделение:"
        },
        "invalid_unit": {
            "en": "Invalid unit!",
            "ru": "Некорректное подразделение!"
        },
        "send_place": {
            "en": "Send place of work:",
            "ru": "Отправьте место работы:"
        },
        "invalid_place": {
            "en": "Invalid place of work!",
            "ru": "Некорректное место работы!"
        },
        "send_phone": {
            "en": "Send phone:",
            "ru": "Отправьте телефон:"
        },
        "invalid_phone": {
            "en": "Invalid phone!",
            "ru": "Некорректный телефон!"
        },
        "send_email": {
            "en": "Send email:",
            "ru": "Отправьте почту:"
        },
        "invalid_email": {
            "en": "Invalid email!",
            "ru": "Некорректная почта!"
        },
        "user_not_unmerged": {
            "en": "User not unmerged!",
            "ru": "Пользователь не разъединен!"
        },
        "user_merge": {
            "en": "Choose user to merge with:",
            "ru": "Выберите пользователя для объединения:"
        },
        "user_not_merged": {
            "en": "User not merged!",
            "ru": "Пользователь не объединен!"
        },
        "admins": {
            "en": "@{bot_username} admins:",
            "ru": "Администраторы @{bot_username}:"
        },
        "required": {
            "en": "Required fields:",
            "ru": "Обязательные поля:"
        },
        "name_is_required": {
            "en": "Name is required!",
            "ru": "Имя обязательно!"
        },
        "not_admin": {
            "en": "You are not bot admin!",
            "ru": "Вы не являетесь администратором бота!"
        },
        "not_user_request": {
            "en": "Requesting access to bot...",
            "ru": "Запрашиваю доступ к боту..."
        },
        "register": {
            "en": "To get access to bot, you need to register...",
            "ru": "Для получения доступа к боту вам необходимо зарегистрироваться..."
        },
        "not_admin_request": {
            "en": "You are not bot admin! Requesting access...",
            "ru": "Вы не являетесь администратором бота! Запрашиваю доступ..."
        },
        "request_user": {
            "en": "User requested access to @{bot_name} with the following data:\n{data}",
            "ru": "Пользователь запросил доступ к @{bot_name} со следующими данными:\n{data}"
        },
        "request_admin": {
            "en": "User <b>{name}</b> requested <b>admin rights</b> to @{bot_name}",
            "ru": "Пользователь <b>{name}</b> запросил <b>права администратора</b> к @{bot_name}"
        },
        "user_accepted": {
            "en": "Your request to access @{bot_name} was accepted!",
            "ru": "Ваш запрос на доступ к @{bot_name} был принят!"
        },
        "admin_accepted": {
            "en": "Your request for <b>admin rights</b> to @{bot_name} was accepted!",
            "ru": "Ваш запрос на <b>права администратора</b> к @{bot_name} был принят!"
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
        "reset": {
            "en": "🔄Reset",
            "ru": "🔄Сбросить"
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
        "add_user": {
            "en": "➕Add User",
            "ru": "➕Добавить пользователя"
        },
        "edit_user_name": {
            "en": "🏷️Edit Name",
            "ru": "🏷️Изменить имя"
        },
        "edit_job_title": {
            "en": "💼Edit Job Title",
            "ru": "💼Изменить должность"
        },
        "edit_unit": {
            "en": "🏢Edit Unit",
            "ru": "🏢Изменить подразделение"
        },
        "edit_place": {
            "en": "📍Edit Place",
            "ru": "📍Изменить место работы"
        },
        "edit_phone": {
            "en": "📞Edit Phone",
            "ru": "📞Изменить телефон"
        },
        "edit_email": {
            "en": "📧Edit Email",
            "ru": "📧Изменить почту"
        },
        "merge": {
            "en": "🔗Merge",
            "ru": "🔗Объединить"
        },
        "unmerge": {
            "en": "⛓️Unmerge",
            "ru": "⛓️Разъединить"
        },
        "admins": {
            "en": "🚨Admins",
            "ru": "🚨Администраторы"
        },
        "required": {
            "en": "🔐Required fields",
            "ru": "🔐Обязательные поля"
        },
        "required_name": {
            "en": "🏷️Name: {status}",
            "ru": "🏷️Имя: {status}"
        },
        "required_job_title": {
            "en": "💼Job Title: {status}",
            "ru": "💼Должность: {status}"
        },
        "required_unit": {
            "en": "🏢Unit: {status}",
            "ru": "🏢Подразделение: {status}"
        },
        "required_place": {
            "en": "📍Place: {status}",
            "ru": "📍Место работы: {status}"
        },
        "required_phone": {
            "en": "📞Phone: {status}",
            "ru": "📞Телефон: {status}"
        },
        "required_email": {
            "en": "📧Email: {status}",
            "ru": "📧Почта: {status}"
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