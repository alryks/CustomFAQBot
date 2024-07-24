from enum import Enum, auto


class State(Enum):
    IDLE = auto()

    ADD_TOKEN = auto()
    EDIT_TOKEN = auto()

    ADD_USER = auto()

    EDIT_NAME = auto()
    EDIT_JOB = auto()
    EDIT_UNIT = auto()
    EDIT_PLACE = auto()
    EDIT_PHONE = auto()
    EDIT_EMAIL = auto()


bots = {}
