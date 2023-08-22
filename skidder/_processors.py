import inspect
import os

import structlog
from structlog.types import WrappedLogger

from skidder import _fields
from skidder._fields import Source


def add_environment_field(_, __, event_dict):
    event_dict[_fields.ENVIRONMENT] = os.getenv("ENV")

    return event_dict


def add_type_field(_, __, event_dict):
    if event_dict[_fields.LEVEL] not in ("warning", "error", "critical"):
        event_dict[_fields.TYPE] = _fields.Type.EVENT
    else:
        event_dict[_fields.TYPE] = _fields.Type.ERROR

    return event_dict


def add_message_field(_, __, event_dict):
    if "ENV" in os.environ:
        event_dict[_fields.MESSAGE] = event_dict.pop("event")

    return event_dict


def add_source_field(source: Source):
    def processor(_, __, event_dict):
        event_dict[_fields.SOURCE] = source

        return event_dict

    return processor


def add_component_field(component: str):
    def processor(_, __, event_dict):
        event_dict[_fields.COMPONENT] = component

        return event_dict

    return processor


def add_location_field(_, __, event_dict):
    # If by any chance the record already contains a `modline` key,
    # (very rare) move that into a 'modline_original' key
    if "modline" in event_dict:
        event_dict["modline_original"] = event_dict["modline"]
    f, name = structlog._frames._find_first_app_frame_and_name(additional_ignores=["logging", __name__])
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


def add_lumigo_prefix(enable_lumigo_prefix: bool):
    def processor(_, __, event_dict):
        if enable_lumigo_prefix and event_dict[_fields.LEVEL] in ("warning", "error", "critical"):
            event_dict[_fields.MESSAGE] = "[LUMIGO_LOG] " + event_dict[_fields.MESSAGE]

        return event_dict

    return processor


def process_exception_field(logger: WrappedLogger, name: str, event_dict: dict):
    if 'exception' not in event_dict:
        return event_dict

    # move to exc_info field to use Structlog's format_exc_info processor
    event_dict["exc_info"] = event_dict.pop("exception")
    event_dict = structlog.processors.format_exc_info(logger, name, event_dict)

    if "exception" in event_dict and "ENV" in os.environ:
        # exc_info was processed, move to stacktrace field, unless local environment
        event_dict["stacktrace"] = event_dict.pop("exception")
    elif "exc_info" in event_dict:
        # exc_info was not processed, move back to exception field
        event_dict["exception"] = event_dict.pop("exc_info")

    return event_dict


def nest_extra_fields_under_data(logger: WrappedLogger, name: str, event_dict: dict):
    new_event_dict = event_dict.copy()
    new_event_dict[_fields.DATA] = {}

    for key in event_dict:
        if key not in [*_fields.ROOT_LEVEL_FIELDS]:
            new_event_dict[_fields.DATA][key] = new_event_dict.pop(key)

    return new_event_dict
