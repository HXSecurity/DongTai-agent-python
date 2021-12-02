import threading
from collections import defaultdict
from contextlib import contextmanager


class ContextTracker(object):
    CURRENT_CONTEXT = "CURRENT_CONTEXT"

    def __init__(self):
        self._tracker = defaultdict(dict)

    def get(self, key, default=None):
        cid = self.current_thread_id()
        if cid == 0 or cid not in self._tracker or key not in self._tracker[cid]:
            return default

        return self._tracker[cid][key]

    def clear(self):
        self._tracker.clear()

    def set(self, key, value):
        cid = self.current_thread_id()
        if cid == 0:
            return
        self._tracker[cid][key] = value

    def delete(self, key):
        cid = self.current_thread_id()

        if cid not in self._tracker or key not in self._tracker[cid]:
            return

        del self._tracker[cid][key]

        if len(self._tracker[cid]) == 0:
            del self._tracker[cid]

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
        tid = threading.get_ident()
        if tid not in threading._active:
            return 0
        return tid
