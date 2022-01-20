import copy
import sys

from dongtai_agent_python.assess import common_hook, c_api_hook
from dongtai_agent_python.assess import ctypes_hook
from dongtai_agent_python.assess_ext import c_api
from dongtai_agent_python.common.logger import logger_config
from dongtai_agent_python.policy import policy
from dongtai_agent_python.setting import const
from dongtai_agent_python.utils import scope

logger = logger_config('assess_patch')


class Namespace(object):
    def __new__(cls, *args, **kwargs):
        raise TypeError("Namespace derivatives may not be instantiated")


class Module(Namespace):
    hook = None


@scope.with_scope(scope.SCOPE_AGENT)
def enable_patches(policies):
    if len(policies) == 0:
        return

    has_patched = {}

    for rules in policies:
        if rules['enable'] != 1 or not rules['details']:
            continue

        for item in rules['details']:
            signature = item['value']

            if signature in has_patched:
                continue

            policy_rule = policy.new_policy_rule(rules['type'], item)
            if policy_rule is None:
                continue

            policy_arr = signature.split(".")

            if signature == 'builtins.eval' or signature == 'builtins.exec':
                method_name = policy_arr[-1]
                new_module = LazyImportHook('builtins', [method_name])
                origin_method = getattr(new_module, method_name)
                origin_cls = new_module.origin_module()

                new_fn = common_hook.build_exec_eval_patch(origin_method, policy_rule)
                origin_cls_ptr = ctypes_hook.magic_get_dict(origin_cls)
                origin_cls_ptr[method_name] = new_fn
                logger.debug("------exec_eval_patch---------- " + "[" + str(rules['type']) + "]" + signature)
                has_patched[signature] = True
                continue
            elif signature in const.C_API_PATCHES:
                c_api_hook.build_callback_function(policy_rule)
                continue

            try:
                imp_arr = copy.deepcopy(policy_arr)
                method_name = imp_arr[-1]
                del imp_arr[-1]
                policy_str = ".".join(imp_arr)
                new_module = LazyImportHook(policy_str, [method_name])
                origin_method = getattr(new_module, method_name)
                origin_cls = new_module.origin_module()
                if origin_cls is None:
                    imp_arr = copy.deepcopy(policy_arr)
                    method_name = imp_arr[-1]
                    class_name = imp_arr[-2]
                    del imp_arr[-1]
                    del imp_arr[-1]
                    policy_str = ".".join(imp_arr)
                    new_module = LazyImportHook(policy_str, [class_name])
                    origin_cls = getattr(new_module, class_name)
            except Exception as e:
                imp_arr = copy.deepcopy(policy_arr)
                if imp_arr[0] not in sys.modules:
                    # print(imp_arr[0])
                    continue

                method_name = imp_arr[-1]
                class_name = imp_arr[-2]
                del imp_arr[-1]
                del imp_arr[-1]
                policy_str = ".".join(imp_arr)

                try:
                    new_module = LazyImportHook(policy_str, [class_name])
                    origin_cls = getattr(new_module, class_name)
                except Exception as e:
                    continue

            after_cls = ctypes_hook.magic_get_dict(origin_cls)

            if isinstance(origin_cls, type):
                hooked = ctypes_hook.build_method_patch(origin_cls, policy_rule)
                if hooked is None:
                    continue
                logger.debug("------origin_cls_property------ " + "[" + str(rules['type']) + "]" + signature)
                after_cls[method_name] = hooked
            else:
                logger.debug("------origin_cls_function------ " + "[" + str(rules['type']) + "]" + signature)
                after_cls[method_name] = common_hook.BuildFuncPatch(origin_method, policy_rule)

            has_patched[signature] = True

    ctypes_hook.magic_flush_mro_cache()

    log = logger_config("assess_ext")
    Module.hook = c_api.initialize(log)
    c_api.enable_patches(Module.hook)
    c_api.install(Module.hook)


class LazyImportHook:
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
