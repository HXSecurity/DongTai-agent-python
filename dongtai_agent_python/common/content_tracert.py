import copy
import hashlib
import os
import re
import sys
import threading
import traceback

import dongtai_agent_python.global_var as dt_global_var
from dongtai_agent_python.common import origin, utils
from dongtai_agent_python.common.default_data import defaultApiData
from dongtai_agent_python.common.utils import recursive_get_hashes

dt_tracker = {}
dt_pool_status = {}
dt_request_id = 0
dt_gid = 0
dt_thread_lock = threading.RLock()
dt_tags = {}


def current_thread_id():
    ident = threading.currentThread().ident
    return str(ident) + str(dt_request_id)


def dt_pool_status_get(default=False):
    try:
        return dt_pool_status[current_thread_id()]
    except KeyError:
        return default


def dt_pool_status_set(value):
    dt_pool_status[current_thread_id()] = value


def dt_tag_get(key, default=False):
    try:
        return dt_tags[current_thread_id()][key]
    except KeyError:
        return default


def dt_tag_set(key, value):
    if current_thread_id() not in dt_tags:
        dt_tags[current_thread_id()] = {}
    dt_tags[current_thread_id()][key] = value


def dt_tracker_get(key, default=None):
    try:
        return dt_tracker[current_thread_id()]['detail'][key]
    except KeyError:
        return default


def dt_tracker_set(key, value):
    dt_tracker[current_thread_id()]['detail'][key] = value


# 将入参格式化
def deal_args(new_args, node_type, end_args=None):
    if end_args is None:
        end_args = []
    for item in new_args:
        if (node_type == utils.NODE_TYPE_SOURCE or
            node_type == utils.NODE_TYPE_PROPAGATOR) and \
                utils.is_empty(item):
            continue

        try:
            item_type = ".".join([type(item).__module__, type(item).__name__])
        except Exception:
            item_type = ''

        hid = utils.get_hash(item)
        if hid not in end_args:
            origin.list_append(end_args, hid)

        if isinstance(item, (tuple, list)):
            end_args = deal_args(item, node_type, end_args)
        elif isinstance(item, dict):
            end_args = deal_args(list(item.values()), node_type, end_args)
        elif item_type == 'django.template.context.RequestContext' or \
                item_type == 'django.template.context.Context':
            for it in item:
                end_args = deal_args([it], node_type, end_args)

    return end_args


def come_in(val, arr):
    if utils.is_empty(val):
        return arr
    hash_id = utils.get_hash(val)

    if hash_id not in arr:
        origin.list_append(arr, hash_id)
    return arr


def recursive_come_in(val, arr):
    if utils.is_empty(val):
        return arr
    hash_id = utils.get_hash(val)

    if hash_id not in arr:
        origin.list_append(arr, hash_id)

    if isinstance(val, (tuple, list)):
        for v in val:
            arr = recursive_come_in(v, arr)
    elif isinstance(val, dict):
        for k in val:
            arr = recursive_come_in(val[k], arr)

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
    try:
        cid = current_thread_id()
        del dt_tracker[cid]
        if cid in dt_pool_status:
            del dt_pool_status[cid]
        if cid in dt_tags:
            del dt_tags[cid]
        dt_thread_lock.release()
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


def method_pool_data(module_name, fcn, sourceValues, taint_in, taint_out, layer=-4, node_type=None, signature=None):
    hook_exit = dt_global_var.dt_get_value("hook_exit")
    # 已检测到危险函数，不再往风险池追加数据
    if hook_exit:
        return False
    tracert = traceback.extract_stack()
    tracert_arr = list(tracert[layer])
    path = sys.path[0]

    if signature == 'django.http.response.HttpResponse.__init__':
        if dt_tag_get('DJANGO_TEMPLATE_RENDER') and not dt_tag_get('HAS_XSS'):
            return False

    not_direct_invoke = [
        'flask.app.Flask.make_response',
        'django.urls.resolvers.RoutePattern.match',
    ]
    while layer > -20:
        tracert_arr = list(tracert[layer])
        if signature in not_direct_invoke:
            break

        if path in tracert_arr[0] and (path + os.sep + "dongtai_agent_python") not in tracert_arr[0]:
            break
        layer = layer - 1


    # bypass flask response for indirect call stack
    if signature not in not_direct_invoke and path not in tracert_arr[0]:
        return False

    # verify xml parser for xxe
    lxml_checks = [
        "lxml.etree.fromstring",
        "lxml.etree.parse",
    ]
    if signature in lxml_checks and tracert_arr[3]:
        if re.search('''XMLParser\\([^)]*resolve_entities\\s*=\\s*False[^)]*\\)''', tracert_arr[3]):
            return False

    have_hooked = dt_global_var.dt_get_value("have_hooked")
    callerMethod = tracert_arr[2]

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

    if signature == 'django.urls.resolvers.RoutePattern.match' and isinstance(taint_out, tuple):
        target_hash = recursive_get_hashes(taint_out)
    else:
        target_hash = [utils.get_hash(taint_out)]
    req_data = {
        "invokeId": 0,
        "interfaces": [],
        "targetHash": target_hash,
        "targetValues": str(taint_out),
        "signature": signature,
        "originClassName": class_name,
        "sourceValues": str(sourceValues),
        "methodName": fcn.__name__,
        "className": class_name,
        "source": node_type == utils.NODE_TYPE_SOURCE,
        "callerLineNumber": tracert_arr[1],
        "callerClass": tracert_arr[0],
        "args": "",
        "callerMethod": callerMethod,
        "sourceHash": taint_in,
        "retClassName": ""
    }
    source_and_target_value = origin.json_dumps({
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
    if node_type == utils.NODE_TYPE_SINK:
        dt_global_var.dt_set_value("hook_exit", True)
