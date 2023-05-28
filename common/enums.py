from enum import Enum

class ResponseStatus(str,Enum):
    ACCEPTED = 'ACCEPTED'
    RUNNING = 'RUNNING'
    ERROR = 'ERROR'
    COMPLETE = 'COMPLETE'
    NOT_FOUND = 'NOT_FOUND'
