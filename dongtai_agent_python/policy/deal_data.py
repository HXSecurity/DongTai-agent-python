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

    if node_type == const.NODE_TYPE_SOURCE:
        context.has_source = True

    tracking = Tracking(signature, node_type, origin_cls, origin_func)
    tracking.apply(come_args, come_kwargs, target)


def filter_result(result, node_type=None):
    if node_type != const.NODE_TYPE_SINK:
        if utils.is_empty(result) or utils.is_not_allowed_type(result):
            return False

    return True
