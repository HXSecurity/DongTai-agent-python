import ctypes
from dongtai_agent_python import global_var as dt_global_var
from dongtai_agent_python.common.content_tracert import dt_tracker_get
from dongtai_agent_python.assess.deal_data import wrapData


class PyObject(ctypes.Structure):
    pass


Py_ssize_t = hasattr(ctypes.pythonapi, 'Py_InitModule4_64') and ctypes.c_int64 or ctypes.c_int

PyObject._fields_ = [
    ('ob_refcnt', Py_ssize_t),
    ('ob_type', ctypes.POINTER(PyObject)),
]


class SlotsPointer(PyObject):
    _fields_ = [('dict', ctypes.POINTER(PyObject))]


def proxy_builtin(klass):
    name = klass.__name__
    # print(name)
    slots = getattr(klass, '__dict__', name)

    pointer = SlotsPointer.from_address(id(slots))
    namespace = {}

    ctypes.pythonapi.PyDict_SetItem(
        ctypes.py_object(namespace),
        ctypes.py_object(name),
        pointer.dict,
    )
    test_a = ctypes.cast(id(slots), ctypes.py_object)
    # print(test_a)
    ctypes.PyDLL(None).PyType_Modified(test_a)
    return namespace[name]


# 普通方法 hook
class InstallFcnHook(object):

    def __init__(self, old_cls, fcn, signature=None, node_type=None):
        self.signature = signature
        self._fcn = fcn
        self.__name__ = fcn.__name__

        self.old_cls = old_cls
        self.node_type = node_type

    def _pre_hook(self, *args, **kwargs):
        # 入参 hook
        if dt_tracker_get("upload_pool"):
            pass
        return (args, kwargs)

    def _post_hook(self, retval, *args, **kwargs):
        # 出参 hook
        return retval

    def __call__(self, *args, **kwargs):

        self._pre_hook(*args, **kwargs)

        if "__bypass_dt_agent__" in kwargs:
            del kwargs["__bypass_dt_agent__"]
            return self._fcn(*args, **kwargs)

        retval = self._fcn(*args, **kwargs)
        if dt_global_var.is_pause():
            return retval

        wrapData(
            retval, self.old_cls.__name__, self._fcn,
            signature=self.signature, node_type=self.node_type, comeData=args, comeKwArgs=kwargs)

        return retval
