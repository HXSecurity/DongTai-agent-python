import ctypes
import os
import sys

from dongtai_agent_python import global_var as dt_global_var
from dongtai_agent_python.assess.deal_data import wrapData


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
def new_func(origin_cls, method_name, signature=None, source=False, *args, **kwargs):
    copy_new_class = type(origin_cls.__name__, origin_cls.__bases__, dict(origin_cls.__dict__))
    _fcn = getattr(origin_cls, method_name)

    def child_func(*args, **kwargs):
        if "__bypass_dt_agent__" in kwargs:
            del kwargs["__bypass_dt_agent__"]
            return _fcn(*args, **kwargs)
        if dt_global_var.dt_get_value("dt_pause"):
            return _fcn(*args, **kwargs)
        if ((args == ([], '*.mo') or args == (['*.mo'], '**')) and method_name == "append") or (
                args == ('**/*.mo', '/') and method_name == "split"):
            return _fcn(*args, **kwargs)
        result = copy_new_class.__dict__[method_name](*args, **kwargs)

        result = wrapData(
            result, origin_cls.__name__, _fcn,
            signature=signature, source=source, comeData=args)

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
