import os
import re
import sys
import traceback

from dongtai_agent_python import CONTEXT_TRACKER
from dongtai_agent_python.setting import const
from dongtai_agent_python.utils import scope, utils


class Tracking(object):
    def __init__(self, signature, node_type, origin_cls, func, layer=-4):
        scope.enter_scope(scope.SCOPE_AGENT)

        self.context = CONTEXT_TRACKER.current()
        self.ignore_tracking = False

        if signature == 'django.http.response.HttpResponse.__init__':
            if self.context.tags.get('TAG_DJANGO_TEMPLATE_RENDER') and not self.context.tags.get('TAG_HAS_XSS'):
                self.ignore_tracking = True
                return

        self.signature = signature
        self.node_type = node_type

        tracert = traceback.extract_stack()
        tracert_arr = list(tracert[layer])
        path = sys.path[0]

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

        # bypass some indirect call stack
        if signature not in not_direct_invoke and path not in tracert_arr[0]:
            self.ignore_tracking = True
            return

        # verify xml parser for xxe
        lxml_checks = [
            "lxml.etree.fromstring",
            "lxml.etree.parse",
        ]
        if signature in lxml_checks and tracert_arr[3]:
            if re.search('''XMLParser\\([^)]*resolve_entities\\s*=\\s*False[^)]*\\)''', tracert_arr[3]):
                self.ignore_tracking = True
                return

        self.class_name = origin_cls
        if signature.endswith("." + func.__name__):
            self.class_name = signature[:-len(func.__name__) - 1]

        self.method_name = func.__name__
        self.caller_class = tracert_arr[0]
        self.caller_line_number = tracert_arr[1]
        self.caller_method = tracert_arr[2]

        scope.exit_scope()

    def apply(self, source, target):
        if self.ignore_tracking or not utils.needs_propagation(self.context, self.node_type):
            return

        source_ids = recurse_tracking(source, self.node_type)

        if self.node_type != const.NODE_TYPE_SOURCE:
            if len(list(set(self.context.taint_ids) & set(source_ids))) == 0:
                return

        source_arr = []
        for src in source:
            try:
                source_arr.append(str(src))
            except Exception:
                continue

        target_ids = recurse_tracking([target], self.node_type)
        for target_id in target_ids:
            if target_id not in self.context.taint_ids:
                self.context.taint_ids.append(target_id)

        pool = {
            "invokeId": len(self.context.pool) + 1,
            "interfaces": [],
            "targetHash": target_ids,
            "targetValues": str(target),
            "signature": self.signature,
            "originClassName": self.class_name,
            "sourceValues": str(source),
            "methodName": self.method_name,
            "className": self.class_name,
            "source": self.node_type == const.NODE_TYPE_SOURCE,
            "callerLineNumber": self.caller_line_number,
            "callerClass": self.caller_class,
            "args": "",
            "callerMethod": self.caller_method,
            "sourceHash": source_ids,
            "retClassName": ""
        }

        self.context.pool.append(pool)
        if self.node_type == const.NODE_TYPE_SINK:
            self.context.hook_exit = True


@scope.with_scope(scope.SCOPE_AGENT)
def recurse_tracking(obj, node_type, hash_ids=None):
    if obj is None:
        return []

    if hash_ids is None:
        hash_ids = []

    for item in obj:
        if (node_type == const.NODE_TYPE_SOURCE or
            node_type == const.NODE_TYPE_PROPAGATOR) and \
                utils.is_empty(item):
            continue

        try:
            item_type = ".".join([type(item).__module__, type(item).__name__])
        except Exception:
            item_type = ''

        hid = utils.get_hash(item)
        if hid not in hash_ids:
            hash_ids.append(hid)

        if isinstance(item, (tuple, list)):
            hash_ids = recurse_tracking(item, node_type, hash_ids)
        elif isinstance(item, dict):
            hash_ids = recurse_tracking(list(item.values()), node_type, hash_ids)
        elif item_type == 'django.template.context.RequestContext' or \
                item_type == 'django.template.context.Context':
            for it in item:
                hash_ids = recurse_tracking([it], node_type, hash_ids)

    return hash_ids
