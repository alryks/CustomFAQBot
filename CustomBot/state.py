from enum import Enum, auto


class State(Enum):
    IDLE = auto()

    FAQ = auto()
    BOOK = auto()

    EDIT_CAPTION = auto()

    ADD_QUESTION = auto()
    ADD_ANSWER = auto()

    EDIT_QUESTION = auto()
    EDIT_ANSWER = auto()