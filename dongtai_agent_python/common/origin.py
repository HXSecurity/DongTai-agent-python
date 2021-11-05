import json

import dongtai_agent_python.global_var as dt_global_var


def str_join(o, value):
    if "builtins.str.join" in dt_global_var.dt_get_value("has_patched"):
        return o.join(value, __bypass_dt_agent__=True)
    return o.join(value)


def list_append(o, value):
    if "builtins.list.append" in dt_global_var.dt_get_value("has_patched"):
        return o.append(value, __bypass_dt_agent__=True)
    return o.append(value)


def json_dumps(value):
    if "json.dumps" in dt_global_var.dt_get_value("has_patched"):
        return json.dumps(value, __bypass_dt_agent__=True)
    return json.dumps(value)
