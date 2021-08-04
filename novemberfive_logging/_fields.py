SOURCE = "source"
TYPE = "type"
COMPONENT = "component"
ENVIRONMENT = "environment"
STACKTRACE = "stacktrace"
REQUEST_ID = "requestId"
LEVEL = "level"
MESSAGE = "message"
DATA = "data"
TIMESTAMP = "timestamp"

ROOT_LEVEL_FIELDS = [
    LEVEL,
    MESSAGE,
    DATA,
    ENVIRONMENT,
    SOURCE,
    TYPE,
    COMPONENT,
    STACKTRACE,
    REQUEST_ID,
    TIMESTAMP
]


class Source:
    APPLICATION = 'application'
    DEPENDENCY = 'dependency'


class Type:
    EVENT = 'event'
    ERROR = 'error'
