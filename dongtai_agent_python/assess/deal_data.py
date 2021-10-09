# hook 参数处理 且 处理污点池
import dongtai_agent_python.global_var as dt_global_var
from dongtai_agent_python.global_var import _global_dt_dict,dt_set_value,dt_get_value
from dongtai_agent_python.common.content_tracert import method_pool_data,dt_tracker_get,dt_tracker_set,come_in,deal_args
import builtins


def wrapData(result, origin_cls, _fcn, signature=None, source=False, comeData=None):
    dt_data_args = dt_tracker_get("dt_data_args")
    if dt_data_args is None:
        return result

    if comeData is None:
        comeData = []
    args = comeData

    dt_open_pool = _global_dt_dict.get("dt_open_pool")
    if dt_open_pool:

        # 污点池
        dt_global_var.dt_set_value("dt_open_pool", False)
        # 入参入池 id
        end_args = deal_args(args)
        # 获取source点
        taint_in = []
        if source:
            can_upload = 1
            for one in end_args:
                dt_data_args = come_in(one, dt_data_args)
                taint_in.append(one)
        else:
            can_upload = 0

            for two in end_args:
                if two in dt_data_args:
                    # hook 当前方法 且 将结果值存入污点池
                    can_upload = 1
                    if two not in taint_in:
                        taint_in.append(two)
            # if not taint_in:
            #     for three in end_args:

        if can_upload == 1:

            # 当前方法type为2、3， callerMethod not in 2、3类其他方法中

            dt_data_args = come_in(result, dt_data_args)
            dt_tracker_set("dt_data_args", dt_data_args)
            method_pool_data(origin_cls, _fcn, args, taint_in, result, source=source, signature=signature)

        dt_global_var.dt_set_value("dt_open_pool", True)
        # except Exception as e:
        #     pass
    return result
