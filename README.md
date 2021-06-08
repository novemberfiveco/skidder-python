# November Five Log Formatting Bundle

## Installation

```
poetry add git+https://github.com/novemberfiveco/logging-standard-python@1.0.0
```

## Usage

In a serverless project, you should create a decorator which will configure the logger. For example;

```from novemberfive_logging.logger import NovemberFiveLogger

def configure_logging(func):
    def configure_logging_wrapper(*args, **kwargs):
        NovemberFiveLogger(root_module_name="project_root_module_name")

        return func(*args, **kwargs)

    return configure_logging_wrapper
```

Make sure to change the name of your projects root module. After this you should decorate all your entrypoints so the
logger gets configured on every lambda function call.

```
@configure_logging
def resolve(event, context):
  ...
```

Now that the logger is configured, just use the `get_logger()` function from structlog to get the correctly configured
logger.

```
from structlog import get_logger

logger = get_logger()

def do_something(*args, **kwargs):
    log = logger.bind(name="some_name")
    ...
    log.info(
        "This is an info log",
        data=args
    )
```

## Releases

- 1.0.0
    - basic setup according to N5 standard.

## Next steps

- Add external library logs
- Catch exceptions and adjust "type" based on this
