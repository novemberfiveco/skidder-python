import contextlib
import logging
import os
import sys
import uuid

import structlog
from structlog import contextvars

from novemberfive_logging import _processors
from novemberfive_logging import _fields


def _get_log_level():
    if os.getenv("LOG_LEVEL") is not None:
        log_level = os.environ['LOG_LEVEL']
    elif os.getenv("ENV") == 'dev':
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    return log_level


def _get_renderer():
    if "ENV" not in os.environ:
        return structlog.dev.ConsoleRenderer()

    return structlog.processors.JSONRenderer(sort_keys=True)


def configure_logging(component=None, log_level: int = _get_log_level()):
    shared_processors = [
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _processors.add_environment_field,
        _processors.add_type_field,
        _processors.add_message_field,
        _processors.add_component_field(component=component),
    ]

    # configure Structlog
    structlog.configure(
        cache_logger_on_first_use=True,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        processors=[
            structlog.contextvars.merge_contextvars,
            *shared_processors,
            _processors.add_source_field(_fields.Source.APPLICATION),
            _processors.process_exception_field,
            _processors.nest_extra_fields_under_data,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter
        ],
        logger_factory=structlog.stdlib.LoggerFactory()
    )

    # configure standard library logging
    stdlib_formatter = structlog.stdlib.ProcessorFormatter(
        processor=_get_renderer(),
        foreign_pre_chain=[
            *shared_processors,
            _processors.add_source_field(_fields.Source.DEPENDENCY)
        ]
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(stdlib_formatter)
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # configure uncaught exception logging
    sys.excepthook = _log_uncaught_exception


def bind_request_id(request_id):
    contextvars.bind_contextvars(**{_fields.REQUEST_ID: request_id})


def unbind_request_id():
    contextvars.unbind_contextvars(*[_fields.REQUEST_ID])


def new_request_id(*args, **kwargs):
    return uuid.uuid4()


def request_context_logging(request_id_provider=new_request_id):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            bind_request_id(request_id_provider(*args, **kwargs))
            fn(*args, **kwargs)
            unbind_request_id()

        return wrapper
    return decorator


def _log_uncaught_exception(exc_type, value, traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # default to builtin excepthook to handle CTRL-C in console
        sys.__excepthook__(exc_type, value, traceback)
        return

    logger = structlog.get_logger()
    logger.error("An uncaught exception occurred", exception=(exc_type, value, traceback))