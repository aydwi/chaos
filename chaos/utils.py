import functools

from random import random
from subprocess import Popen, TimeoutExpired, DEVNULL


def Xstatus():
    """Return a bool indicating whether an X server is running or not"""
    try:
        proc = Popen(["xset", "q"], stdout=DEVNULL,
                                    stderr=DEVNULL)
    except OSError:
        return False
    try:
        proc.communicate(timeout=4)
    except TimeoutExpired:
        proc.kill()
        proc.communicate()
    return proc.returncode == 0


def randomhit(flag):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if random() < 0.5:
                func(*args, **kwargs)
        if flag:
            return wrapper
        else:
            return func
    return decorator
