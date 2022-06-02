from functools import wraps


def lock(_lock):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _lock.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                _lock.release()
        return wrapper
    return decorator
