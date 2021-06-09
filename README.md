# November Five Log Formatting Bundle

## Installation

```
poetry add git+https://github.com/novemberfiveco/logging-standard-python@1.0.0
```

## Usage

The library exposes a decorator you should use on all your entrypoints so the
logger gets configured on every lambda function call.

```
from novemberfive_logging.decorator import configure_logging

@configure_logging
def resolve(event, context):
  ...
```

Now that the logger is configured, just use the `get_logger()` function from structlog to get the correctly configured
logger anywhere inside your project.

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
