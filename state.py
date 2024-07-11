from enum import Enum, auto


class State(Enum):
    IDLE = auto()
    TOKEN = auto()
    QUESTION = auto()
    ANSWER = auto()


bots = {}
