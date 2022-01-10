import threading
from contextlib import contextmanager

SCOPE_AGENT = 'agent'


class ScopeContext(threading.local):
    def __init__(self):
        self._active_scopes = []

    @property
    def active_scopes(self):
        return self._active_scopes[:]

    @property
    def current_scope(self):
        if len(self._active_scopes) == 0:
            return ''
        return self._active_scopes[-1][:]  # Slice to get copy.

    def enter_scope(self, name):
        """Enters the given scope, updating the list of active scopes.
        Args:
          name: scope name
        """
        self._active_scopes = self._active_scopes + [name]

    def exit_scope(self):
        """Exits the most recently entered scope."""
        self._active_scopes = self._active_scopes[:-1]

    def in_scope(self, name):
        return name in self._active_scopes


SCOPE_CONTEXT = ScopeContext()


@contextmanager
def scope(name):
    SCOPE_CONTEXT.enter_scope(name)
    try:
        yield
    finally:
        SCOPE_CONTEXT.exit_scope()


def with_scope(name):
    def wrapper(original_func):
        def _wrapper(*args, **kwargs):
            with scope(name):
                return_value = original_func(*args, **kwargs)
            return return_value
        return _wrapper
    return wrapper


def current_scope():
    return SCOPE_CONTEXT.current_scope


def enter_scope(name):
    return SCOPE_CONTEXT.enter_scope(name)


def exit_scope():
    return SCOPE_CONTEXT.exit_scope()


def in_scope(name):
    return SCOPE_CONTEXT.in_scope(name)
