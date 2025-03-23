from enum import Enum, auto


class State(Enum):
    IDLE = auto()

    REPORT = auto()
    REPORT_FEEDBACK = auto()

    NAME = auto()
    JOB_TITLE = auto()
    UNIT = auto()
    PLACE = auto()
    PERSONAL_PHONE = auto()
    WORK_PHONE = auto()
    ADDITIONAL_NUMBER = auto()
    EMAIL = auto()

    EDIT_NAME = auto()
    EDIT_SUPERVISOR = auto()
    EDIT_JOB = auto()
    EDIT_UNIT = auto()
    EDIT_PLACE = auto()
    EDIT_PERSONAL_PHONE = auto()
    EDIT_WORK_PHONE = auto()
    EDIT_ADDITIONAL_NUMBER = auto()
    EDIT_EMAIL = auto()

    FAQ = auto()
    CONTACTS = auto()
    
    # Состояния для функционала "Приведи друга"
    FRIEND = auto()
    FRIEND_SELECT_JOB = auto()
    FRIEND_NAME = auto()
    FRIEND_REFERRAL = auto()
    FRIEND_GENDER = auto()
    FRIEND_PHONE = auto()
    FRIEND_AGE = auto()
    FRIEND_DATE_ON_OBJECT = auto()
    FRIEND_RESIDENCE = auto()
    FRIEND_PHOTO = auto()
    FRIEND_EDIT = auto()

    ADD_QUESTION = auto()
    ADD_ANSWER = auto()

    EDIT_QUESTION = auto()
    EDIT_ANSWER = auto()