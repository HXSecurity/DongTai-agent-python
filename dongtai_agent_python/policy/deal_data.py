from dongtai_agent_python import CONTEXT_TRACKER
from dongtai_agent_python.policy.tracking import Tracking
from dongtai_agent_python.setting import const
from dongtai_agent_python.utils import scope, utils


@scope.with_scope(scope.SCOPE_AGENT)
def wrap_data(target, origin_cls, origin_func, signature=None, node_type=None, come_args=None, come_kwargs=None):
    context = CONTEXT_TRACKER.current()
    if not utils.needs_propagation(context, node_type):
        return

    if not filter_result(target, node_type):
        return

    invoke_args = processing_invoke_args(signature, come_args, come_kwargs)

    if node_type == const.NODE_TYPE_SOURCE:
        context.has_source = True

    tracking = Tracking(signature, node_type, origin_cls, origin_func)
    tracking.apply(invoke_args, target)


def filter_result(result, node_type=None):
    if node_type != const.NODE_TYPE_SINK and utils.is_empty(result):
        return False

    if node_type == const.NODE_TYPE_SOURCE:
        if utils.is_not_allowed_type(result):
            return False

    return True


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
    }

    context = CONTEXT_TRACKER.current()
    if signature == 'django.template.base.render_value_in_context':
        try:
            item = come_args[1]
            item_type = ".".join([type(item).__module__, type(item).__name__])
            if item_type == 'django.template.context.RequestContext' or \
                    item_type == 'django.template.context.Context':
                context.tags['TAG_DJANGO_TEMPLATE_RENDER'] = True
                if not item.autoescape:
                    context.tags['TAG_HAS_XSS'] = True
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
