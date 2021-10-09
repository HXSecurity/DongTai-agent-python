import ctypes,sys
from dongtai_agent_python.global_var import _global_dt_dict,dt_set_value,dt_get_value
from dongtai_agent_python.common.content_tracert import method_pool_data,dt_tracker_get,dt_tracker_set,come_in,deal_args
import dongtai_agent_python.global_var as dt_global_var
from dongtai_agent_python.assess.deal_data import wrapData
import sqlite3
copyStr = type('str', str.__bases__, dict(str.__dict__))


def magic_get_dict(o):
    # find address of dict whose offset is stored in the type
    dict_addr = id(o) + type(o).__dictoffset__
    # retrieve the dict object itself
    dict_ptr = ctypes.cast(dict_addr, ctypes.POINTER(ctypes.py_object))
    return dict_ptr.contents.value


def magic_flush_mro_cache():
    ctypes.PyDLL(None).PyType_Modified(ctypes.cast(id(object), ctypes.py_object))


# 属性方法hook
def new_func(origin_cls, method_name, signature=None, source=False, *args, **kwargs):

    copyNewClass = type(origin_cls.__name__, origin_cls.__bases__, dict(origin_cls.__dict__))
    _fcn = getattr(origin_cls, method_name)
    # print(copyNewStr.__dict__)

    def child_func(*args, **kwargs):
        if ( (args == ([],'*.mo') or args == (['*.mo'], '**') ) and method_name=="append" ) or (args == ('**/*.mo', '/') and method_name=="split" ):
            return _fcn(*args, **kwargs)
        result = copyNewClass.__dict__[method_name](*args, **kwargs)

        result = wrapData(
            result, origin_cls.__name__, _fcn,
            signature=signature,source=source, comeData=args)

        return result
    return child_func


class hookLazyImport:
    def __init__(self, module_name,fromlist=[]):
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
