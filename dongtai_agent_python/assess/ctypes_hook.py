import ctypes
import os
import sys

from dongtai_agent_python.policy.deal_data import wrap_data
from dongtai_agent_python.setting import const
from dongtai_agent_python.utils import scope


# https://stackoverflow.com/a/24498525
def magic_get_dict(o):
    # find address of dict whose offset is stored in the type
    dict_addr = id(o) + type(o).__dictoffset__
    # retrieve the dict object itself
    dict_ptr = ctypes.cast(dict_addr, ctypes.POINTER(ctypes.py_object))
    return dict_ptr.contents.value


def magic_flush_mro_cache():
    if os.name == "nt":
        pythonapi = ctypes.PyDLL("python dll", None, sys.dllhandle)
    elif sys.platform == "cygwin":
        pythonapi = ctypes.PyDLL("libpython%d.%d.dll" % sys.version_info[:2])
    else:
        pythonapi = ctypes.PyDLL(None)

    pythonapi.PyType_Modified(ctypes.py_object(object))


# 属性方法hook
def new_func(origin_cls, method_name, signature=None, node_type=None, *args, **kwargs):
    copy_new_class = type(origin_cls.__name__, origin_cls.__bases__, dict(origin_cls.__dict__))
    if method_name not in copy_new_class.__dict__:
        return None
    origin_func = getattr(origin_cls, method_name)

    def child_func(*args, **kwargs):
        if node_type == const.NODE_TYPE_FILTER:
            with scope.scope(scope.SCOPE_AGENT):
                result = copy_new_class.__dict__[method_name](*args, **kwargs)
        else:
            result = copy_new_class.__dict__[method_name](*args, **kwargs)
        if scope.in_scope(scope.SCOPE_AGENT):
            return result

        wrap_data(
            result, origin_cls.__name__, origin_func.__name__,
            signature=signature, node_type=node_type,
            come_args=args, come_kwargs=kwargs)

        return result

    return child_func


class HookLazyImport:
    def __init__(self, module_name, fromlist=None):
        self.module_name = module_name
        self.module = None
        if fromlist:
            self.fromlist = fromlist
        else:
            self.fromlist = []

    def __getattr__(self, name):
        if self.module is None:
            self.module = __import__(self.module_name, globals(), locals(), self.fromlist, 0)

        return getattr(self.module, name)

    def origin_module(self):
        return self.module
