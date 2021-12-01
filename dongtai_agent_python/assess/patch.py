import copy
import sys

from dongtai_agent_python.assess.common_hook import InstallFcnHook
from dongtai_agent_python.assess.ctypes_hook import HookLazyImport, magic_flush_mro_cache, magic_get_dict, new_func
from dongtai_agent_python.setting import Setting
from dongtai_agent_python.utils import scope


@scope.with_scope(scope.SCOPE_AGENT)
def enable_patches(policies):
    if len(policies) == 0:
        return

    setting = Setting()
    has_patched = {}
    for rules in policies:
        if rules['enable'] != 1 or not rules['details']:
            continue

        for item in rules['details']:
            policy = item['value']
            policy_arr = policy.split(".")

            if policy in has_patched:
                continue

            try:
                imp_arr = copy.deepcopy(policy_arr)
                method_name = imp_arr[-1]
                setting.policy[method_name] = rules['type']
                # 存储到全局变量
                del imp_arr[-1]
                policy_str = ".".join(imp_arr)
                old_module = HookLazyImport(policy_str, [method_name])
                old_func = getattr(old_module, method_name)
                old_cls = old_module.origin_module()
                if old_cls is None:
                    imp_arr = copy.deepcopy(policy_arr)
                    method_name = imp_arr[-1]
                    class_name = imp_arr[-2]
                    del imp_arr[-1]
                    del imp_arr[-1]
                    policy_str = ".".join(imp_arr)
                    old_module = HookLazyImport(policy_str, [class_name])
                    old_cls = getattr(old_module, class_name)
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
                    old_module = HookLazyImport(policy_str, [class_name])
                    old_cls = getattr(old_module, class_name)
                except Exception as e:
                    continue

            after_cls = magic_get_dict(old_cls)

            if isinstance(old_cls, type):
                hooked = new_func(
                    old_cls,
                    method_name,
                    policy,
                    rules['type']
                )
                if hooked is None:
                    continue
                if setting.config.get("debug"):
                    print("------origin_cls_property------ " + "[" + str(rules['type']) + "]" + policy)
                after_cls[method_name] = hooked
            else:
                if setting.config.get("debug"):
                    print("------origin_cls_function------ " + "[" + str(rules['type']) + "]" + policy)
                after_cls[method_name] = InstallFcnHook(old_cls, old_func, policy, rules['type'])

            has_patched[policy] = True

    magic_flush_mro_cache()
