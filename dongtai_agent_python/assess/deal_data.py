# hook 参数处理 且 处理污点池
import dongtai_agent_python.global_var as dt_global_var
from dongtai_agent_python.common import origin, utils
from dongtai_agent_python.global_var import _global_dt_dict
from dongtai_agent_python.common.content_tracert import method_pool_data, dt_tracker_get, dt_tracker_set, come_in, \
    deal_args


def wrapData(result, origin_cls, _fcn, signature=None, node_type=None, comeData=None, comeKwArgs=None):
    if node_type != utils.NODE_TYPE_SINK and utils.is_empty(result):
        return result

    if node_type == utils.NODE_TYPE_SOURCE:
        if utils.is_not_allowed_type(result):
            return result

    dt_open_pool = _global_dt_dict.get("dt_open_pool")
    if not dt_open_pool:
        return result

    dt_global_var.dt_set_value("dt_open_pool", False)

    dt_data_args = dt_tracker_get("dt_data_args")
    if dt_data_args is None:
        return result

    invokeArgs = []
    if comeData is not None:
        for v in comeData:
            origin.list_append(invokeArgs, v)
    if comeKwArgs is not None:
        for k in comeKwArgs:
            origin.list_append(invokeArgs, comeKwArgs[k])

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
            for two in end_args:
                if two in dt_data_args:
                    # hook 当前方法 且 将结果值存入污点池
                    can_upload = 1
                    if two not in taint_in:
                        origin.list_append(taint_in, two)

    if can_upload == 1:
        if len(dt_data_args) != 0:
            dt_data_args = come_in(result, dt_data_args)
            dt_tracker_set("dt_data_args", dt_data_args)
            method_pool_data(origin_cls, _fcn, invokeArgs, taint_in, result, node_type=node_type, signature=signature)

    dt_global_var.dt_set_value("dt_open_pool", True)

    return result
