import logging
import pickle
import sys
from contextlib import contextmanager
from multiprocessing import Lock

from dongtai_agent_python.utils.lock import lock

if sys.version_info[:3] <= (3, 7):
    from shared_memory.shared_memory import SharedMemory
else:
    from multiprocessing.shared_memory import SharedMemory

NULL_BYTE = b"\x00"

logger = logging.getLogger(__name__)
_lock = Lock()
DEFAULT_OBJ = object()


class SharedMemoryDict:
    def __init__(self, name, size=1024):
        self.name = name
        self.mem_block = self.get_or_create(size)
        self.init_memory()

    @lock(_lock)
    def get_or_create(self, size):
        try:
            return SharedMemory(name=self.name)
        except FileNotFoundError:
            return SharedMemory(name=self.name, create=True, size=size)

    def init_memory(self):
        memory_is_empty = (bytes(self.mem_block.buf).split(NULL_BYTE, 1)[0] == b'')
        if memory_is_empty:
            self.save_memory({})

    def close(self) -> None:
        if not hasattr(self, 'mem_block'):
            return
        self.mem_block.close()

    def unlink(self) -> None:
        if not hasattr(self, 'mem_block'):
            return
        self.mem_block.unlink()

    @lock
    def clear(self) -> None:
        self.save_memory({})

    def popitem(self):
        with self.modify_db() as db:
            return db.popitem()

    def save_memory(self, db) -> None:
        data = pickle.dumps(db)
        try:
            self.mem_block.buf[:len(data)] = data
        except ValueError as exc:
            logging.error("failed save to memory", exc_info=exc)

    def read_memory(self):
        return pickle.loads(self.mem_block.buf.tobytes())

    @contextmanager
    @lock(_lock)
    def modify_db(self):
        db = self.read_memory()
        yield db
        self.save_memory(db)

    def __getitem__(self, key: str):
        return self.read_memory()[key]

    def __setitem__(self, key: str, value) -> None:
        with self.modify_db() as db:
            db[key] = value

    def __len__(self) -> int:
        return len(self.read_memory())

    def __delitem__(self, key: str) -> None:
        with self.modify_db() as db:
            del db[key]

    def __iter__(self):
        return iter(self.read_memory())

    def __reversed__(self):
        return reversed(self.read_memory())

    def __del__(self) -> None:
        self.close()

    def __contains__(self, key: str) -> bool:
        return key in self.read_memory()

    def __eq__(self, other) -> bool:
        return self.read_memory() == other

    def __ne__(self, other) -> bool:
        return self.read_memory() != other

    if sys.version_info > (3, 8):
        def __or__(self, other):
            return self.read_memory() | other

        def __ror__(self, other):
            return other | self.read_memory()

        def __ior__(self, other):
            with self.modify_db() as db:
                db |= other
                return db

    def __str__(self):
        return str(self.read_memory())

    def __repr__(self):
        return repr(self.read_memory())

    def get(self, key: str, default=None):
        return self.read_memory().get(key, default)

    def keys(self):
        return self.read_memory().keys()

    def values(self):
        return self.read_memory().values()

    def items(self):
        return self.read_memory().items()

    def pop(self, key: str, default=DEFAULT_OBJ):
        with self.modify_db() as db:
            if default is DEFAULT_OBJ:
                return db.pop(key)
            return db.pop(key, default)

    def update(self, other=(), **kwargs):
        with self.modify_db() as db:
            db.update(other, **kwargs)

    def setdefault(self, key: str, default=None):
        with self.modify_db() as db:
            return db.setdefault(key, default)
