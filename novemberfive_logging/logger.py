import inspect
import logging
import os
from functools import lru_cache

import structlog
from structlog._frames import _find_first_app_frame_and_name
from structlog.contextvars import merge_contextvars


LOGGING_SOURCE_APPLICATION = "application"
LOGGING_SOURCE_LIBRARY = "library"
LOGGING_SOURCE_DEPENDENCY = "dependency"


# TODO: Also catch exceptions!
class NovemberFiveLogger:
    @lru_cache()
    def __init__(self, log_level: str = None):
        structlog.configure(
            cache_logger_on_first_use=True,
            wrapper_class=structlog.make_filtering_bound_logger(log_level or logging.INFO),
            processors=[
                merge_contextvars,
                structlog.threadlocal.merge_threadlocal_context,
                structlog.processors.add_log_level,
                structlog.processors.format_exc_info,
                self.show_module_info_processor,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                self._add_environment,
                self._add_type,
                self._add_source,
                self._rename_event_to_message,
                structlog.processors.JSONRenderer(sort_keys=True),
            ],
        )

    def _add_environment(self, _, __, event_dict):
        event_dict["environment"] = os.getenv("ENV")

        return event_dict

    # TODO: make dynamic
    def _add_type(self, _, __, event_dict):
        event_dict["type"] = "event"

        return event_dict

    # TODO: make dynamic
    def _add_source(self, _, __, event_dict):
        event_dict["source"] = LOGGING_SOURCE_APPLICATION

        return event_dict

    def _rename_event_to_message(self, _, __, event_dict):
        event_dict["message"] = event_dict["event"]
        event_dict.pop("event")

        return event_dict

    def show_module_info_processor(self, logger, _, event_dict):
        # If by any chance the record already contains a `modline` key,
        # (very rare) move that into a 'modline_original' key
        if "modline" in event_dict:
            event_dict["modline_original"] = event_dict["modline"]
        f, name = _find_first_app_frame_and_name(additional_ignores=["logging", __name__])
        if not f:
            return event_dict
        frameinfo = inspect.getframeinfo(f)
        if not frameinfo:
            return event_dict
        module = inspect.getmodule(f)
        if not module:
            return event_dict
        if frameinfo and module:
            event_dict["file"] = "{}:{}".format(module.__name__, frameinfo.lineno)

        return event_dict
