import os
import re
import sys
import traceback

from pkg_resources import parse_version

from dongtai_agent_python import CONTEXT_TRACKER
from dongtai_agent_python.setting import const
from dongtai_agent_python.utils import scope, utils


class Tracking(object):
    def __init__(self, signature, node_type, origin_cls, func_name):
        scope.enter_scope(scope.SCOPE_AGENT)

        self.context = CONTEXT_TRACKER.current()
        self.ignore_tracking = False

        if signature in const.RESPONSE_SIGNATURES:
            if self.context.tags.get('TAG_TEMPLATE_RENDER') and self.context.tags.get('TAG_HTML_ENCODED'):
                self.ignore_tracking = True
                scope.exit_scope()
                return

        self.signature = signature
        self.node_type = node_type

        self.class_name = origin_cls
        if signature.endswith("." + func_name):
            self.class_name = signature[:-len(func_name) - 1]

        self.method_name = func_name
        self.caller_class = ''
        self.caller_line_number = ''
        self.caller_method = ''

        scope.exit_scope()

    @scope.scope(scope.SCOPE_AGENT)
    def get_caller(self, layer):
        tracert = traceback.extract_stack()
        tracert_arr = list(tracert[layer])
        path = sys.path[0]

        not_direct_invoke = [
            'flask.app.Flask.make_response',
            'django.urls.resolvers.RoutePattern.match',
        ]
        while layer > -20:
            tracert_arr = list(tracert[layer])
            if self.signature in not_direct_invoke:
                break

            if path in tracert_arr[0] and \
                    (path + os.sep + "dongtai_agent_python") not in tracert_arr[0] and \
                    ("site-packages" + os.sep + "dongtai_agent_python") not in tracert_arr[0]:
                break
            layer = layer - 1

        # bypass some indirect call stack
        if self.signature not in not_direct_invoke and path not in tracert_arr[0]:
            self.ignore_tracking = True
            return

        # verify xml parser for xxe
        lxml_checks = [
            "lxml.etree.fromstring",
            "lxml.etree.parse",
        ]
        if self.signature in lxml_checks and tracert_arr[3]:
            if re.search('''XMLParser\\([^)]*resolve_entities\\s*=\\s*False[^)]*\\)''', tracert_arr[3]):
                self.ignore_tracking = True
                return

        self.caller_class = tracert_arr[0]
        self.caller_line_number = tracert_arr[1]
        self.caller_method = tracert_arr[2]

    @scope.scope(scope.SCOPE_AGENT)
    def apply(self, args, kwargs, target):
        if self.ignore_tracking or not utils.needs_propagation(self.context, self.node_type):
            return

        if (self.signature == 'yaml.load' or self.signature == 'yaml.load_all') and yaml_load_is_safe(args, kwargs):
            return

        source = processing_invoke_args(self.signature, args, kwargs)
        # @TODO: improve performance
        source_ids = recurse_tracking(source, self.node_type)

        if self.node_type != const.NODE_TYPE_SOURCE:
            if self.signature in const.CRYPTO_BAD_CIPHER_NEW:
                pass
            elif (self.signature.startswith('Crypto.Cipher._mode_') or
                  self.signature.startswith('Cryptodome.Cipher._mode_')) and \
                    self.signature.endswith('Mode.encrypt'):
                for sid in source_ids:
                    if sid not in self.context.taint_ids:
                        return
            elif len(list(set(self.context.taint_ids) & set(source_ids))) == 0:
                return

        self.get_caller(-4)
        if self.ignore_tracking:
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


def processing_invoke_args(signature=None, come_args=None, come_kwargs=None):
    sink_args = {
        'sqlite3.Cursor.execute': {'args': [1]},
        'sqlite3.Cursor.executemany': {'args': [1]},
        'sqlite3.Cursor.executescript': {'args': [1]},
        'psycopg2._psycopg.cursor.execute': {'args': [1], 'kwargs': ['query']},
        'psycopg2._psycopg.cursor.executemany': {'args': [1], 'kwargs': ['query']},
        'MySQLdb.cursors.BaseCursor.execute': {'args': [1], 'kwargs': ['query']},
        'MySQLdb.cursors.BaseCursor.executemany': {'args': [1], 'kwargs': ['query']},
        'pymysql.cursors.Cursor.execute': {'args': [1], 'kwargs': ['query']},
        'pymysql.cursors.Cursor.executemany': {'args': [1], 'kwargs': ['query']},
        'mysql.connector.cursor.CursorBase.execute': {'args': [1], 'kwargs': ['operation']},
        'mysql.connector.cursor.CursorBase.executemany': {'args': [1], 'kwargs': ['operation']},
        'pymongo.collection.Collection.find': {'args': [1], 'kwargs': ['filter']},
        'ldap3.core.connection.Connection.search': {'args': [2], 'kwargs': ['search_filter']},
        'ldap.ldapobject.SimpleLDAPObject.search_ext': {'args': [3], 'kwargs': ['filterstr']},
        'Crypto.Cipher._mode_cbc.CbcMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
        'Crypto.Cipher._mode_cfb.CfbMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
        'Crypto.Cipher._mode_ctr.CtrMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
        'Crypto.Cipher._mode_eax.EaxMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
        'Crypto.Cipher._mode_ecb.EcbMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
        'Crypto.Cipher._mode_ofb.OfbMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
        'Crypto.Cipher._mode_openpgp.OpenPgpMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
        'Cryptodome.Cipher._mode_cbc.CbcMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
        'Cryptodome.Cipher._mode_cfb.CfbMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
        'Cryptodome.Cipher._mode_ctr.CtrMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
        'Cryptodome.Cipher._mode_eax.EaxMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
        'Cryptodome.Cipher._mode_ecb.EcbMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
        'Cryptodome.Cipher._mode_ofb.OfbMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
        'Cryptodome.Cipher._mode_openpgp.OpenPgpMode.encrypt': {'args': [0, 1], 'kwargs': ['plaintext']},
    }

    context = CONTEXT_TRACKER.current()
    if signature == 'django.template.base.render_value_in_context':
        try:
            item = come_args[1]
            item_type = ".".join([type(item).__module__, type(item).__name__])
            if item_type == 'django.template.context.RequestContext' or \
                    item_type == 'django.template.context.Context':
                context.tags['TAG_TEMPLATE_RENDER'] = True
                if not item.autoescape:
                    context.tags['TAG_HTML_ENCODED'] = False
        except Exception:
            pass

    invoke_args = []
    if signature not in sink_args:
        if come_args is not None:
            for v in come_args:
                invoke_args.append(v)
        if come_kwargs is not None:
            for k in come_kwargs:
                invoke_args.append(come_kwargs[k])

        return invoke_args

    if come_args and len(come_args) > 0 and 'args' in sink_args[signature]:
        args_size = len(come_args)
        for arg in sink_args[signature]['args']:
            if args_size > arg:
                invoke_args.append(come_args[arg])

    if come_kwargs and len(come_kwargs) > 0 and 'kwargs' in sink_args[signature]:
        for key in sink_args[signature]['kwargs']:
            if key in come_kwargs:
                invoke_args.append(come_kwargs[key])

    return invoke_args


def yaml_load_is_safe(args, kwargs=None):
    if kwargs is None:
        kwargs = {}

    try:
        import yaml
        if parse_version(yaml.__version__) < parse_version('5.1'):
            if len(args) < 2 and 'Loader' not in kwargs:
                return False
    except ImportError:
        pass

    if len(args) == 2:
        if args[1].__name__ == 'UnsafeLoader':
            return False
    if 'Loader' in kwargs:
        if kwargs['Loader'].__name__ == 'UnsafeLoader':
            return False
    return True


@scope.with_scope(scope.SCOPE_AGENT)
def recurse_tracking(obj, node_type, hash_ids=None):
    if obj is None:
        return []

    if hash_ids is None:
        hash_ids = []

    for item in obj:
        if utils.is_empty(item) or utils.is_not_allowed_type(item):
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
