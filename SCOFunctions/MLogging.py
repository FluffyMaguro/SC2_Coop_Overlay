import datetime
import functools
import threading
import traceback
from enum import Enum

lock = threading.Lock()


class LogLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4


class Logger:
    """ Custom class for logging purposes """
    LOGGING = False
    file_path = "Logs.txt"
    levels = LogLevel

    def __init__(self, name: str, level: LogLevel):
        self.name = name
        self.level = level

        if not isinstance(level, LogLevel):
            raise Exception(f'Logging level has to be of type {type(LogLevel)}')

    def printsave(self, mtype: str, message: str) -> None:
        time = datetime.datetime.now().strftime("%d/%m %H:%M:%S")
        msg = f'{time} - {self.name:4} ({mtype}): {message}'
        try:
            print(msg)
        except Exception:
            try:
                print(msg.encode("utf-8"))
            except Exception:
                print(traceback.format_exc())

        if self.LOGGING:
            with lock, open(self.file_path, 'ab') as f:
                f.write(f'{msg}\n'.encode())

    def debug(self, message: str) -> None:
        if self.level.value > LogLevel.DEBUG.value:
            return
        self.printsave('debug', message)

    def info(self, message: str) -> None:
        if self.level.value > LogLevel.INFO.value:
            return
        self.printsave('info', message)

    def warning(self, message: str) -> None:
        if self.level.value > LogLevel.WARNING.value:
            return
        self.printsave('warning', message)

    def error(self, message: str) -> None:
        self.printsave('ERROR', message)


def catch_exceptions(logger: Logger):
    """ Catches exceptions for given function and writes a log"""

    # Outer function is here to provide argument for the decorator
    def inner_function(job_func):
        @functools.wraps(job_func)  # passes useful info to decorators
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except Exception:
                logger.error(traceback.format_exc())

        return wrapper

    return inner_function
