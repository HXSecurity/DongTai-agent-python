import copy
import hashlib
import json
import os
import sys
import threading
import traceback

import dongtai_agent_python.global_var as dt_global_var
from dongtai_agent_python.common import origin
from dongtai_agent_python.common.default_data import defaultApiData

dt_tracker = {}
dt_request_id = 0
dt_gid = 0
dt_thread_lock = threading.RLock()


def current_thread_id():
    ident = threading.currentThread().ident
    return str(ident) + str(dt_request_id)


def dt_tracker_get(key, default=None):
    try:
        return dt_tracker[current_thread_id()]['detail'][key]
    except KeyError:
        return default


def dt_tracker_set(key, value):
    dt_tracker[current_thread_id()]['detail'][key] = value


# 将入参格式化
def deal_args(new_args, end_args=None):
    if end_args is None:
        end_args = []
    for item in new_args:
        origin.list_append(end_args, id(item))

        if isinstance(item, tuple):
            end_args = deal_args(item, end_args)

    return end_args


def come_in(val, arr):
    hash_id = id(val)

    if hash_id not in arr:
        origin.list_append(arr, hash_id)
    return arr


def delete(key):
    thread_id = current_thread_id()

    if thread_id not in dt_tracker.keys():
        return

    del dt_tracker[thread_id]['detail'][key]

    if len(dt_tracker[thread_id]) == 0:
        del dt_tracker[thread_id]


def set_current(request_id):
    global dt_request_id, dt_thread_lock
    dt_thread_lock.acquire()
    dt_request_id = request_id
    dt_tracker[current_thread_id()] = copy.deepcopy(defaultApiData)


def delete_current():
    global dt_thread_lock
    dt_thread_lock.release()
    try:
        del dt_tracker[current_thread_id()]
    except Exception:
        pass


def current():
    current_thread = threading.currentThread()
    return dt_tracker[current_thread]


def append_method_pool(value):
    global dt_gid
    dt_gid = dt_gid + 1
    value['invokeId'] = dt_gid
    try:
        method_pool = dt_tracker[current_thread_id()].get("detail", {}).get("pool", [])
        origin.list_append(method_pool, value)
        return True
    except Exception:
        return False


def method_pool_data(module_name, fcn, sourceValues, taint_in, taint_out, layer=-4, source=False, signature=None):
    hook_exit = dt_global_var.dt_get_value("hook_exit")
    # 已检测到危险函数，不再往风险池追加数据
    if hook_exit:
        return False
    tracert = traceback.extract_stack()
    tracert_arr = list(tracert[layer])
    path = sys.path[0]
    while layer > -20:
        tracert_arr = list(tracert[layer])
        if path in tracert_arr[0] and (path + os.sep + "dongtai_agent_python") not in tracert_arr[0]:
            break
        layer = layer - 1

    if path not in tracert_arr[0]:
        return False
    policy_global = dt_global_var.dt_get_value("policy")

    have_hooked = dt_global_var.dt_get_value("have_hooked")
    callerMethod = tracert_arr[2]
    method_type = policy_global.get(callerMethod, 0)
    cur_type = policy_global.get(fcn.__name__, 0)

    if (method_type == 2 or method_type == 3) and cur_type != 4:
        return False

    source_arr = []
    for one in sourceValues:
        try:
            origin.list_append(source_arr, str(one))
        except Exception:
            continue

    if signature.endswith("." + fcn.__name__):
        class_name = signature[:-len(fcn.__name__) - 1]
    else:
        class_name = module_name
    req_data = {
        "invokeId": 0,
        "interfaces": [],
        "targetHash": [
            id(taint_out)
        ],
        "targetValues": str(taint_out),
        "signature": signature,
        "originClassName": class_name,
        "sourceValues": str(sourceValues),
        "methodName": fcn.__name__,
        "className": class_name,
        "source": source,
        "callerLineNumber": tracert_arr[1],
        "callerClass": tracert_arr[0],
        "args": "",
        "callerMethod": callerMethod,
        "sourceHash": taint_in,
        "retClassName": ""
    }
    source_and_target_value = json.dumps({
        "sourceHash": req_data['sourceHash'],
        "targetHash": req_data['targetHash']
    })
    hl = hashlib.md5()
    hl.update(source_and_target_value.encode(encoding='utf-8'))
    afterMd5Id = hl.hexdigest()

    if afterMd5Id not in have_hooked:
        append_method_pool(req_data)
        origin.list_append(have_hooked, afterMd5Id)
        dt_global_var.dt_set_value("have_hooked", have_hooked)
    if cur_type == 4:
        dt_global_var.dt_set_value("hook_exit", True)
