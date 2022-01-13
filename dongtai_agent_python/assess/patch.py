import copy
import sys

from dongtai_agent_python.assess.common_hook import InstallFcnHook, build_exec_eval_patch
from dongtai_agent_python.assess.ctypes_hook import HookLazyImport, magic_flush_mro_cache, magic_get_dict, new_func
from dongtai_agent_python.assess_ext import c_api
from dongtai_agent_python.common.logger import logger_config
from dongtai_agent_python.setting import Setting, const
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

    setting = Setting()
    has_patched = {}

    log = logger_config("assess_ext")
    Module.hook = c_api.initialize(log)

    c_api.enable_patches(Module.hook)
    c_api.install(Module.hook)

    for rules in policies:
        if rules['enable'] != 1 or not rules['details']:
            continue

        for item in rules['details']:
            policy = item['value']
            policy_arr = policy.split(".")

            if policy in has_patched:
                continue

            if policy == 'builtins.eval' or policy == 'builtins.exec':
                method_name = policy_arr[-1]
                new_module = HookLazyImport('builtins', [method_name])
                origin_func = getattr(new_module, method_name)
                origin_cls = new_module.origin_module()

                new_fn = build_exec_eval_patch(origin_cls, origin_func, policy, rules['type'])
                origin_cls_ptr = magic_get_dict(origin_cls)
                origin_cls_ptr[method_name] = new_fn
                logger.debug("------exec_eval_patch---------- " + "[" + str(rules['type']) + "]" + policy)
                has_patched[policy] = True
                continue
            elif policy in const.C_API_PATCHES:
                # patch by C extension
                continue

            try:
                imp_arr = copy.deepcopy(policy_arr)
                method_name = imp_arr[-1]
                del imp_arr[-1]
                policy_str = ".".join(imp_arr)
                new_module = HookLazyImport(policy_str, [method_name])
                origin_func = getattr(new_module, method_name)
                origin_cls = new_module.origin_module()
                if origin_cls is None:
                    imp_arr = copy.deepcopy(policy_arr)
                    method_name = imp_arr[-1]
                    class_name = imp_arr[-2]
                    del imp_arr[-1]
                    del imp_arr[-1]
                    policy_str = ".".join(imp_arr)
                    new_module = HookLazyImport(policy_str, [class_name])
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
                    new_module = HookLazyImport(policy_str, [class_name])
                    origin_cls = getattr(new_module, class_name)
                except Exception as e:
                    continue

            after_cls = magic_get_dict(origin_cls)

            if isinstance(origin_cls, type):
                hooked = new_func(
                    origin_cls,
                    method_name,
                    policy,
                    rules['type']
                )
                if hooked is None:
                    continue
                logger.debug("------origin_cls_property------ " + "[" + str(rules['type']) + "]" + policy)
                after_cls[method_name] = hooked
            else:
                logger.debug("------origin_cls_function------ " + "[" + str(rules['type']) + "]" + policy)
                after_cls[method_name] = InstallFcnHook(origin_cls, origin_func, policy, rules['type'])

            has_patched[policy] = True

    magic_flush_mro_cache()
