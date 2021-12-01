import ctypes
import os
import sys

from dongtai_agent_python import CONTEXT_TRACKER
from dongtai_agent_python.policy.deal_data import wrap_data
from dongtai_agent_python.utils import utils
from dongtai_agent_python.setting import const, Setting
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
    origin_fcn = getattr(origin_cls, method_name)

    def child_func(*args, **kwargs):
        result = copy_new_class.__dict__[method_name](*args, **kwargs)
        if scope.in_scope(scope.SCOPE_AGENT):
            return result

        context = CONTEXT_TRACKER.current()
        if not utils.needs_propagation(context, node_type):
            return result

        setting = Setting()
        if setting.is_agent_paused():
            return result

        if ((args == ([], '*.mo') or args == (['*.mo'], '**')) and method_name == "append") or (
                args == ('**/*.mo', '/') and method_name == "split"):
            return result

        # some method first args is self and is also used to return the value
        extra_in = None
        if signature in const.FIRST_RETURN and len(args) > 0:
            extra_in = [{
                'index': 0,
                'value': str(args[0]),
                'hash': utils.get_hash(args[0]),
            }]

        if signature in const.FIRST_RETURN and len(args) > 0:
            real_result = args[0]
        else:
            real_result = result

        with scope.scope(scope.SCOPE_AGENT):
            come_args = []
            for k, v in enumerate(args):
                if signature in const.FIRST_RETURN and k == 0:
                    continue
                come_args.append(v)

        wrap_data(
            result, origin_cls.__name__, origin_fcn,
            signature=signature, node_type=node_type,
            come_args=come_args, come_kwargs=kwargs,
            extra_in=extra_in, real_result=real_result)

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
