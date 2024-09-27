from telegram import Update

from typing import Union


class Languages:
    langs = [
        "en",
        "ru"
    ]

    _cmd = {
        "start": {
            "en": "Launch bot",
            "ru": "Запуск бота"
        },
        "help": {
            "en": "Bot help",
            "ru": "Информация о работе с ботом"
        },
        "faq": {
            "en": "Frequently Asked Questions",
            "ru": "Часто задаваемые вопросы"
        },
        "contacts": {
            "en": "Employee contacts",
            "ru": "Контакты сотрудников"
        }
    }

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
        "faq": {
            "en": "<b>Frequently Asked Questions:</b>",
            "ru": "<b>Часто задаваемые вопросы:</b>"
        },
        "contacts_caption": {
            "en": "<b>Employee contacts:</b>",
            "ru": "<b>Контакты сотрудников:</b>"
        },
        "similar_users": {
            "en": "<b>Employees with similar data already exist without a linked Telegram account:</b>",
            "ru": "<b>С похожими данными уже есть сотрудники без привязанного Telegram аккаунта:</b>"
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
            "en": "<i>Full name:</i> {name}",
            "ru": "<i>ФИО:</i> {name}"
        },
        "supervisor": {
            "en": "<i>Supervisor:</i> {supervisor}",
            "ru": "<i>Руководитель:</i> {supervisor}"
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
        "personal_phone": {
            "en": "<i>Personal Phone:</i> {phone}",
            "ru": "<i>Личный телефон:</i> {phone}"
        },
        "work_phone": {
            "en": "<i>Work Phone:</i> {phone}",
            "ru": "<i>Рабочий телефон:</i> {phone}"
        },
        "additional_number": {
            "en": "<i>Additional Number:</i> {number}",
            "ru": "<i>Добавочный номер:</i> {number}"
        },
        "email": {
            "en": "<i>Email:</i> {email}",
            "ru": "<i>Почта:</i> {email}"
        },
        "telegram": {
            "en": "<i>Telegram:</i> {telegram}",
            "ru": "<i>Телеграм:</i> {telegram}"
        },
        "send_report": {
            "en": "Describe what data is incorrect in text form:",
            "ru": "Опишите, какие данные неверны, в текстовой форме:"
        },
        "report_sent": {
            "en": "Your report has been sent!",
            "ru": "Ваш запрос отправлен!"
        },
        "report": {
            "en": "<b>A report about incorrect data has been sent:</b>\n\n{report}",
            "ru": "<b>Было отправлено сообщение о неверных данных:</b>\n\n{report}"
        },
        "send_feedback": {
            "en": "Describe your feedback in text form:",
            "ru": "Напишите сообщение для обратной связи в текстовой форме:"
        },
        "report_closed": {
            "en": "The report has been closed!",
            "ru": "Запрос уже закрыт!"
        },
        "feedback": {
            "en": "<b>Feedback on your report:</b>\n\n{feedback}",
            "ru": "<b>Обратная связь по вашему запросу:</b>\n\n{feedback}"
        },
        "supervisors": {
            "en": "<b>Choose a supervisor:</b>",
            "ru": "<b>Выберите руководителя:</b>"
        },
        "send_name": {
            "en": "Send full name:",
            "ru": "Отправьте ФИО:"
        },
        "invalid_name": {
            "en": "Invalid name!",
            "ru": "Некорректное ФИО!"
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
        "send_personal_phone": {
            "en": "Send personal phone:",
            "ru": "Отправьте личный телефон:"
        },
        "invalid_personal_phone": {
            "en": "Invalid personal phone!",
            "ru": "Некорректный личный телефон!"
        },
        "send_work_phone": {
            "en": "Send work phone:",
            "ru": "Отправьте рабочий телефон:"
        },
        "invalid_work_phone": {
            "en": "Invalid work phone!",
            "ru": "Некорректный рабочий телефон!"
        },
        "send_additional_number": {
            "en": "Send additional number:",
            "ru": "Отправьте добавочный номер:"
        },
        "invalid_additional_number": {
            "en": "Invalid additional number!",
            "ru": "Некорректный добавочный номер!"
        },
        "send_email": {
            "en": "Send email:",
            "ru": "Отправьте почту:"
        },
        "invalid_email": {
            "en": "Invalid email!",
            "ru": "Некорректная почта!"
        },
        "user_confirm_delete": {
            "en": "Are you sure you want to delete this employee?",
            "ru": "Вы уверены, что хотите удалить этого сотрудника?"
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
        "request_user": {
            "en": "User requested access to the bot with the following data:\n{data}",
            "ru": "Пользователь запросил доступ к боту со следующими данными:\n{data}"
        },
        "already_requested": {
            "en": "You have already requested access to боту!",
            "ru": "Вы уже запросили доступ к боту!"
        },
        "user_accepted": {
            "en": "Your request to access the bot was accepted!",
            "ru": "Ваш запрос на доступ к боту был принят!"
        },
        "user_denied": {
            "en": "Your request to access the bot was denied!",
            "ru": "Ваш запрос на доступ к боту был отклонен!"
        },
        "edit_true": {
            "en": "You ENTERED edit mode!",
            "ru": "Вы ВОШЛИ в режим редактирования!"
        },
        "edit_false": {
            "en": "You EXITED edit mode!",
            "ru": "Вы ВЫШЛИ из режима редактирования!"
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
        "add_user": {
            "en": "➕Add Employee",
            "ru": "➕Добавить сотрудника"
        },
        "to_user": {
            "en": "👤To Employee",
            "ru": "👤К сотруднику"
        },
        "report": {
            "en": "🚨Report incorrect data",
            "ru": "🚨Сообщить о неверных данных"
        },
        "report_feedback": {
            "en": "✅Accept",
            "ru": "✅Принять"
        },
        "edit_user_name": {
            "en": "🏷Full Name",
            "ru": "🏷ФИО"
        },
        "edit_job_title": {
            "en": "💼Job Title",
            "ru": "💼Должность"
        },
        "edit_unit": {
            "en": "🏢Unit",
            "ru": "🏢Подразделение"
        },
        "edit_place": {
            "en": "📍Place",
            "ru": "📍Место работы"
        },
        "edit_supervisor": {
            "en": "👥Supervisor",
            "ru": "👥Руководитель"
        },
        "edit_personal_phone": {
            "en": "📱Personal Phone",
            "ru": "📱Личный телефон"
        },
        "edit_work_phone": {
            "en": "📞Work Phone",
            "ru": "📞Рабочий телефон"
        },
        "edit_additional_number": {
            "en": "☎Additional Number",
            "ru": "☎Добавочный номер"
        },
        "edit_email": {
            "en": "📧Email",
            "ru": "📧Почта"
        },
        "user_admin": {
            "en": "🚨Admin: {admin}",
            "ru": "🚨Админ: {admin}"
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
    def get(cls, field: str, key: str, update: Union[Update, str]) -> str:
        lang = update.effective_user.language_code if isinstance(update, Update) else update
        text_langs: dict = cls.__dict__[field].get(key)
        if text_langs is None:
            return ""

        if lang in text_langs:
            return text_langs.get(lang)

        return sorted(text_langs.items(), key=lambda x: cls.langs.index(x[0]))[0][1]

    @classmethod
    def cmd(cls, key: str, lang: str) -> str:
        return cls.get("_cmd", key, lang)

    @classmethod
    def msg(cls, key: str, update: Update) -> str:
        return cls.get("_msg", key, update)

    @classmethod
    def btn(cls, key: str, update: Update) -> str:
        return cls.get("_btn", key, update)

    @classmethod
    def kbd(cls, key: str, update: Update) -> str:
        return cls.get("_kbd", key, update)