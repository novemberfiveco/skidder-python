import json
import logging
import os

import structlog

from novemberfive_logging import configure_logging, request_context_logging


def test_structlog_logging(capsys):
    os.environ["ENV"] = "prod"
    configure_logging(component="test")
    log = structlog.get_logger()

    try:
        raise RuntimeError("Oops")
    except RuntimeError as e:
        log.critical("Something bad happened!", exception=e)

    captured_output = capsys.readouterr()
    print(captured_output.out)
    event = json.loads(captured_output.out)

    assert captured_output.err == ""
    assert event["component"] == "test"
    assert event["type"] == "error"


def test_stdlib_logging(capsys):
    os.environ["ENV"] = "prod"
    configure_logging(component="test")
    log = logging.getLogger()

    try:
        raise RuntimeError("Oops")
    except RuntimeError as e:
        log.critical("Something bad happened!")

    captured_output = capsys.readouterr()
    event = json.loads(captured_output.out)

    assert captured_output.err == ""
    assert event["component"] == "test"
    assert event["type"] == "error"


def test_request_context_logging(capsys):
    os.environ["ENV"] = "prod"
    configure_logging(component="test")
    log = structlog.get_logger()

    def request_id_provider(event, context):
        return context

    @request_context_logging(request_id_provider=request_id_provider)
    def handler(event, context):
        try:
            raise RuntimeError("Oops")
        except RuntimeError as e:
            log.critical("Something bad happened!", exception=e)

    handler(object(), 'request-123')

    captured_output = capsys.readouterr()
    event = json.loads(captured_output.out)

    assert captured_output.err == ""
    assert event["component"] == "test"
    assert event["type"] == "error"
    assert event["requestId"] == "request-123"