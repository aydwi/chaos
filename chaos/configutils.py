import functools

from random import random

def random_hit_chance_util(flag):
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
