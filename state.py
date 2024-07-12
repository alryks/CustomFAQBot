from enum import Enum, auto


class State(Enum):
    IDLE = auto()
    ADD_TOKEN = auto()
    EDIT_TOKEN = auto()
    ADD_QUESTION = auto()
    EDIT_QUESTION = auto()
    ADD_ANSWER = auto()
    EDIT_ANSWER = auto()


bots = {}
