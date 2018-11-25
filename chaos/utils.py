import functools

from random import random


def randomhit(flag):
    def decorator(func):
        @functools.wraps(func)
        def decorated_func(*args, **kwargs):
            if random() < 0.5:
                func(*args, **kwargs)
        if flag:
            return decorated_func
        else:
            return func
    return decorator
