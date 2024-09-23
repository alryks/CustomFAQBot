from enum import Enum, auto


class State(Enum):
    IDLE = auto()

    NAME = auto()
    JOB_TITLE = auto()
    UNIT = auto()
    PLACE = auto()
    PHONE = auto()
    EMAIL = auto()

    EDIT_NAME = auto()
    EDIT_JOB = auto()
    EDIT_UNIT = auto()
    EDIT_PLACE = auto()
    EDIT_PHONE = auto()
    EDIT_EMAIL = auto()

    FAQ = auto()
    CONTACTS = auto()

    ADD_QUESTION = auto()
    ADD_ANSWER = auto()

    EDIT_QUESTION = auto()
    EDIT_ANSWER = auto()