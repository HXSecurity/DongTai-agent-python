# hook 参数处理 且 处理污点池
from dongtai_agent_python.common import origin, utils
from dongtai_agent_python.common.content_tracert import dt_pool_status_get, dt_pool_status_set, dt_tag_set, \
    method_pool_data, \
    dt_tracker_get, \
    dt_tracker_set, come_in, \
    deal_args, recursive_come_in


def wrapData(result, origin_cls, _fcn, signature=None, node_type=None, comeData=None, comeKwArgs=None, extra_in=None, real_result=None):
    if not filter_result(real_result, node_type):
        return result

    dt_open_pool = dt_pool_status_get()
    if not dt_open_pool:
        return result

    dt_pool_status_set(False)

    dt_data_args = dt_tracker_get("dt_data_args")
    if dt_data_args is None:
        return result

    invokeArgs = processing_invoke_args(signature, comeData, comeKwArgs)

    # 获取source点
    taint_in = []
    if node_type == utils.NODE_TYPE_SOURCE:
        can_upload = 1
        # 入参入池 id
        end_args = deal_args(invokeArgs, node_type)
        for one in end_args:
            dt_data_args = come_in(one, dt_data_args)
            origin.list_append(taint_in, one)
    else:
        can_upload = 0

        # source is not empty
        if len(dt_data_args) != 0:
            # 入参入池 id
            end_args = deal_args(invokeArgs, node_type)
            if extra_in:
                for ein in extra_in:
                    origin.list_append(end_args, ein["hash"])
                    origin.list_insert(invokeArgs, ein["index"], ein["value"])
            for two in end_args:
                if two in dt_data_args:
                    # hook 当前方法 且 将结果值存入污点池
                    can_upload = 1
                    if two not in taint_in:
                        origin.list_append(taint_in, two)

    if can_upload == 1:
        if len(dt_data_args) != 0:
            if signature == 'django.urls.resolvers.RoutePattern.match':
                dt_data_args = recursive_come_in(real_result, dt_data_args)
            else:
                dt_data_args = come_in(real_result, dt_data_args)
            dt_tracker_set("dt_data_args", dt_data_args)
            method_pool_data(origin_cls, _fcn, invokeArgs, taint_in, real_result, node_type=node_type, signature=signature)

    dt_pool_status_set(True)

    return result


def filter_result(result, node_type=None):
    if node_type != utils.NODE_TYPE_SINK and utils.is_empty(result):
        return False

    if node_type == utils.NODE_TYPE_SOURCE:
        if utils.is_not_allowed_type(result):
            return False

    return True


def processing_invoke_args(signature=None, comeData=None, comeKwArgs=None):
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

    if signature == 'django.template.base.render_value_in_context':
        try:
            item = comeData[1]
            item_type = ".".join([type(item).__module__, type(item).__name__])
            if item_type == 'django.template.context.RequestContext' or \
                    item_type == 'django.template.context.Context':
                dt_tag_set('DJANGO_TEMPLATE_RENDER', True)
                if not item.autoescape:
                    dt_tag_set('HAS_XSS', True)
        except Exception:
            pass

    invokeArgs = []
    if signature not in sink_args:
        if comeData is not None:
            for v in comeData:
                origin.list_append(invokeArgs, v)
        if comeKwArgs is not None:
            for k in comeKwArgs:
                origin.list_append(invokeArgs, comeKwArgs[k])

        return invokeArgs

    if comeData and len(comeData) > 0 and 'args' in sink_args[signature]:
        args_size = len(comeData)
        for arg in sink_args[signature]['args']:
            if args_size > arg:
                origin.list_append(invokeArgs, comeData[arg])

    if comeKwArgs and len(comeKwArgs) > 0 and 'kwargs' in sink_args[signature]:
        for key in sink_args[signature]['kwargs']:
            if key in comeKwArgs:
                origin.list_append(invokeArgs, comeKwArgs[key])

    return invokeArgs
