import copy
import sys

import dongtai_agent_python.global_var as dt_global_var
from dongtai_agent_python.common import origin
from dongtai_agent_python.common.common_hook import InstallFcnHook
from dongtai_agent_python.common.ctypes_hook import HookLazyImport, magic_flush_mro_cache, magic_get_dict, new_func
from dongtai_agent_python.report.upload_data import AgentUpload


def enable_patches(cur_frame_app="django"):
    config_data = dt_global_var.dt_get_value("config_data")
    # 通过api读取策略信息
    agent_req = AgentUpload()
    policy_info = agent_req.get_policy_config()
    policy_global = dt_global_var.dt_get_value("policy")
    frame_app = ["django", "flask", "tornado", "bottle"]
    # 测试环境 本地读取
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    # file_path = os.path.join(base_dir, '../policy_api.json')
    # with open(file_path, 'r') as load_f:
    #     policy_info = json.load(load_f)

    if policy_info.get("status", 0) != 201:
        return

    for rules in policy_info['data']:
        if rules['enable'] != 1 or not rules['details']:
            continue

        has_patched = {}
        if rules['type'] == 2:
            source = True
        else:
            source = False
        for item in rules['details']:
            policy = item['value']
            policy_arr = policy.split(".")
            if policy_arr[0] in frame_app and policy_arr[0] != cur_frame_app:
                continue

            try:
                imp_arr = copy.deepcopy(policy_arr)
                method_name = imp_arr[-1]
                policy_global[method_name] = rules['type']
                # 存储到全局变量
                del imp_arr[-1]
                policy_str = origin.str_join(".", imp_arr)
                old_module = HookLazyImport(policy_str, [method_name])
                old_func = getattr(old_module, method_name)
                old_cls = old_module.origin_module()
                if old_cls is None:
                    imp_arr = copy.deepcopy(policy_arr)
                    method_name = imp_arr[-1]
                    class_name = imp_arr[-2]
                    del imp_arr[-1]
                    del imp_arr[-1]
                    policy_str = origin.str_join(".", imp_arr)
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
                policy_str = origin.str_join(".", imp_arr)

                try:
                    old_module = HookLazyImport(policy_str, [class_name])
                    old_cls = getattr(old_module, class_name)
                except Exception as e:
                    continue

            if policy in has_patched:
                continue

            after_cls = magic_get_dict(old_cls)

            if isinstance(old_cls, type):
                if config_data.get("debug"):
                    print("------origin_cls_property------ " + policy)
                after_cls[method_name] = new_func(
                    old_cls,
                    method_name,
                    policy,
                    source
                )
            else:
                if config_data.get("debug"):
                    print("------origin_cls_function------ " + policy)
                after_cls[method_name] = InstallFcnHook(old_cls, old_func, policy, source)

            has_patched[policy] = True
            dt_global_var.dt_set_value("has_patched", has_patched)

    dt_global_var.dt_set_value("policy", policy_global)
    # print("hook == success")
    magic_flush_mro_cache()
