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
def build_method_patch(origin_cls, policy_rule, *args, **kwargs):
    copy_new_class = type(origin_cls.__name__, origin_cls.__bases__, dict(origin_cls.__dict__))
    if policy_rule.method_name not in copy_new_class.__dict__:
        return None
    origin_method = getattr(origin_cls, policy_rule.method_name)
    policy_rule.set_origin_method(origin_method)

    def child_func(*args, **kwargs):
        if policy_rule.node_type == const.NODE_TYPE_FILTER:
            with scope.scope(scope.SCOPE_AGENT):
                result = copy_new_class.__dict__[policy_rule.method_name](*args, **kwargs)
        else:
            result = copy_new_class.__dict__[policy_rule.method_name](*args, **kwargs)
        if scope.in_scope(scope.SCOPE_AGENT):
            return result

        wrap_data(policy_rule, result=result, come_args=args, come_kwargs=kwargs)

        return result

    policy_rule.set_patched_method(child_func)

    return child_func

