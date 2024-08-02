from enum import Enum, auto


class State(Enum):
    IDLE = auto()

    ADD_TOKEN = auto()
    EDIT_TOKEN = auto()


bots = {}
