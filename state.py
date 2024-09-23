from enum import Enum, auto


class State(Enum):
    IDLE = auto()

    NAME = auto()
    JOB_TITLE = auto()
    UNIT = auto()
    PLACE = auto()
    PERSONAL_PHONE = auto()
    WORK_PHONE = auto()
    ADDITIONAL_NUMBER = auto()
    EMAIL = auto()

    EDIT_NAME = auto()
    EDIT_JOB = auto()
    EDIT_UNIT = auto()
    EDIT_PLACE = auto()
    EDIT_PERSONAL_PHONE = auto()
    EDIT_WORK_PHONE = auto()
    EDIT_ADDITIONAL_NUMBER = auto()
    EDIT_EMAIL = auto()

    FAQ = auto()
    CONTACTS = auto()

    ADD_QUESTION = auto()
    ADD_ANSWER = auto()

    EDIT_QUESTION = auto()
    EDIT_ANSWER = auto()