from enum import Enum


# A Response Status enum for task status endpoint.
class ResponseStatus(str, Enum):
    ACCEPTED = 'ACCEPTED'
    RUNNING = 'RUNNING'
    ERROR = 'ERROR'
    COMPLETE = 'COMPLETE'
    NOT_FOUND = 'NOT_FOUND'
