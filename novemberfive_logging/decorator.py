from novemberfive_logging.logger import NovemberFiveLogger


def configure_logging(func):
    def configure_logging_wrapper(*args, **kwargs):
        NovemberFiveLogger()

        return func(*args, **kwargs)

    return configure_logging_wrapper
