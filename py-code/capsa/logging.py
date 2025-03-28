import logging
from typing_extensions import Literal

__LOG_ENABLED = True


def cprint(*values: object, sep: str | None = " ", end: str | None = "\n"):
    if __LOG_ENABLED:
        print(*values, sep=sep, end=end)


def disable_log():
    global __LOG_ENABLED
    __LOG_ENABLED = False


def enable_log():
    global __LOG_ENABLED
    __LOG_ENABLED = True
