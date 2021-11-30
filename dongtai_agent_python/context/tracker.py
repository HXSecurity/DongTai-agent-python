import threading
from contextlib import contextmanager
from collections import defaultdict


class ContextTracker(object):
    CURRENT_CONTEXT = "CURRENT_CONTEXT"

    def __init__(self):
        self._tracker = defaultdict(dict)

    def get(self, key, default=None):
        cid = self.current_thread_id()
        if cid not in self._tracker or key not in self._tracker[cid]:
            return default

        return self._tracker[cid][key]

    def clear(self):
        self._tracker.clear()

    def set(self, key, value):
        self._tracker[self.current_thread_id()][key] = value

    def delete(self, key):
        current_thread_id = self.current_thread_id()

        if current_thread_id not in self._tracker or key not in self._tracker[current_thread_id]:
            return

        del self._tracker[current_thread_id][key]

        if len(self._tracker[current_thread_id]) == 0:
            del self._tracker[current_thread_id]

    def set_current(self, value):
        self.set(self.CURRENT_CONTEXT, value)

    def delete_current(self):
        self.delete(self.CURRENT_CONTEXT)

    @contextmanager
    def lifespan(self, context):
        self.set_current(context)

        yield context

        self.delete_current()

    def current(self):
        return self.get(self.CURRENT_CONTEXT)

    def current_thread_id(self):
        return threading.currentThread().ident
