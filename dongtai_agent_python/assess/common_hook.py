import ctypes

from dongtai_agent_python import CONTEXT_TRACKER
from dongtai_agent_python.policy.deal_data import wrap_data
from dongtai_agent_python.setting import const, Setting
from dongtai_agent_python.utils import scope, utils


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

    def __call__(self, *args, **kwargs):
        ret_val = self._fcn(*args, **kwargs)

        if scope.in_scope(scope.SCOPE_AGENT):
            return ret_val

        context = CONTEXT_TRACKER.current()
        if not utils.needs_propagation(context, self.node_type):
            return ret_val

        with scope.scope(scope.SCOPE_AGENT):
            setting = Setting()
        if setting.is_agent_paused():
            return ret_val

        wrap_data(
            ret_val, self.old_cls.__name__, self._fcn,
            signature=self.signature, node_type=self.node_type,
            come_args=args, come_kwargs=kwargs,
            extra_in=None, real_result=ret_val)

        return ret_val
