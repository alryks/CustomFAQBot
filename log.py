import time
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from telegram import User

from db import UsersDb

from config import SPREADSHEET_ID, SPREADSHEET_RANGE

adding_row = False

# Словарь для расшифровки действий
ACTION_DESCRIPTIONS = {
    "unregistered": "Нет доступа",
    "accept": "Принят",
    "deny": "Отклонен", 
    "start": "Старт",
    "faq": "FAQ",
    "faq_ans": "Просмотр вопроса",
    "contacts": "Контакты",
    "contact": "Просмотр контакта",
    "report": "Сообщение об ошибке",
    "report_text": "Текст исправления",
    "register": "Регистрация"
}

def format_values(*values):
    """Форматирует значения согласно требованиям"""
    if not values:
        return ["", ""]
    elif len(values) == 1:
        return [str(values[0]), ""]
    elif len(values) == 2:
        return [str(values[0]), str(values[1])]
    else:
        return [str(values[0]), "; ".join(str(v) for v in values[1:])]

def add_row(row):
    global adding_row
    while adding_row:
        time.sleep(5)
    adding_row = True

    creds = Credentials.from_service_account_file("credentials.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
    value_input_option = "RAW"

    try:
        service = build("sheets", "v4", credentials=creds)

        values = [
            row
        ]
        body = {"values": values}

        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=SPREADSHEET_ID,
                range=SPREADSHEET_RANGE,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
    except HttpError as error:
        print(f"An error occurred: {error}")

    adding_row = False

def log_action(user: User, action: str, *data):
    current_time = datetime.now()
    current_date = current_time.strftime("%Y-%m-%d")
    current_time = current_time.strftime("%H:%M:%S")

    user_obj = UsersDb.get_user_by_tg(user.id)
    if user_obj:
        user_name = user_obj["name"]
        user_supervisor = UsersDb.get_user(user_obj["supervisor"])
        user_supervisor_name = user_supervisor["name"] if user_supervisor else ""
        user_job_title = user_obj["job_title"]
        user_unit = user_obj["unit"]
        user_place = user_obj["place"]
        user_work_phone = user_obj["work_phone"]
        user_additional_number = user_obj["additional_number"] if user_obj["additional_number"] else ""
    else:
        user_name = user.full_name
        user_supervisor_name = ""
        user_job_title = ""
        user_unit = ""
        user_place = ""
        user_work_phone = ""
        user_additional_number = ""

    # Получаем описание действия
    action_description = ACTION_DESCRIPTIONS.get(action, action)
    
    # Форматируем значения
    value1, value2 = format_values(*data)

    # Формируем строку для записи в таблицу в новом порядке
    row = [
        current_date,           # Дата
        current_time,          # Время 
        user_name,             # ФИО
        action,                # Действие
        action_description,    # Расшифровка действия
        value1,                # Значение 1
        value2,                # Значение 2
        user.id,              # Остальные поля
        user.username,
        user_supervisor_name,
        user_job_title,
        user_unit, 
        user_place,
        user_work_phone,
        user_additional_number
    ]

    add_row(row)
