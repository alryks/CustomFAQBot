from enum import Enum, auto


class State(Enum):
    IDLE = auto()

    NAME = auto()
    JOB_TITLE = auto()
    UNIT = auto()
    PLACE = auto()
    PHONE = auto()
    EMAIL = auto()

    FAQ = auto()
    CONTACTS = auto()

    EDIT_CAPTION = auto()

    ADD_QUESTION = auto()
    ADD_ANSWER = auto()

    EDIT_QUESTION = auto()
    EDIT_ANSWER = auto()