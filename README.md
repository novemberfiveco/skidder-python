# November Five Log Formatting Bundle

## Installation
```commandline
poetry add git+https://github.com/novemberfiveco/logging-standard-python@2.0.1
```

## Usage

### Setup

Configure logging using the `configure_logging()` function once at the beginning of your program.
You can pass a value for the `component` field as required by N5's standards.
```python
from novemberfive_logging import configure_logging

configure_logging(component='my-backend-service')

# note that we configure logging outside the AWS Lambda handler function
def handler(event, context):
    ...
 
```

### Logging events

Now that the logger is configured, just use the `get_logger()` function from *structlog* to get the correctly configured
logger anywhere inside your project.

```python
from structlog import get_logger

log = get_logger()

log.debug("This is a debug log")
log.info("This is an info log")
log.warn("This is a warn log")
log.error("This is an error log")
log.critical("This is a critical log")
```

When running this program locally, you receive pretty formatted log output:

````commandline
2021-07-12T18:04:48.248064Z [info     ] This is an info log                             component=foo environment=None source=application type=event
````

However, in an actual environment, you should set the `ENV` environment variable, which will enable JSON logging:

````json5
{"component": "foo", "environment": "dev", "level": "info", "message": "This is an info log", "source": "application", "timestamp": "2021-07-12T18:07:08.674527Z", "type": "event"}
````

### Logging exceptions

You can pass an exception parameter to include a stacktrace in the log event:

````python
try:
    raise Exception
except Exception as e:
    log.error("API call to external service X failed due to timeout", exception=e)
````

### Including additional fields

You can also pass extra parameters to populate the `data` field with additional structured information:

````python
log.info("Synchronizing product catalog to store", store_id='store-123')
````


### Setting a request ID on your log events

Whenever possible, you should set the `requestId` field on log events to link them to a specific request for easy investigation.

You can manually set or unset:

```python
from structlog import bind_request_id, unbind_request_id

log.info("This log event is not part of a request")

def handler(event, context):
    bind_request_id("my-request-123")
    log.info("This log event is part of my-request-123")
    unbind_request_id()
```

For convenience, there is also a decorator that automatically (un)binds a request ID whenever your function is called. By default, a new UUID is generated.
```python
from structlog import request_context_logging

log.info("This log event is not part of a request")

@request_context_logging
def handler(event, context):
    log.info("This log event is part of a request")
```

You can also pass a function that provides the request ID (for example you might want to get it from an HTTP request header
to continue a request spanning multiple distributed services):
```python
from structlog import request_context_logging

log.info("This log event is not part of a request")

def request_id_from_header(event, context):
    return event["headers"]["X-Trace-ID"]

@request_context_logging(request_id_provider=request_id_from_header)
def handler(event, context):
    log.info("This log event is part of a request")
```

## Changelog

- 2.0.1
  - Added check for IS_LOCAL env variable to check local development env
- 2.0.0
    - Pin structlog dependency (because using private function that is not part of public structlog API and can change without notice)
    - Set minimum logging level to DEBUG when in dev environment
    - Log uncaught exceptions
    - Intercept & process STDLIB logging
    - Populate type field dynamically
    - Populate source field dynamically
    - Refactor into functions
    - Allow binding request ID field
    - Allow binding component field
    - Disable JSON logging & enable pretty logging when executing locally
    - Nest extra fields under the 'data' key
- 1.0.0
    - basic setup according to N5 standard.

