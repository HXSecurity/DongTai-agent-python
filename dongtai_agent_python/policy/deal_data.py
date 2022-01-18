from dongtai_agent_python import CONTEXT_TRACKER
from dongtai_agent_python.policy.tracking import Tracking
from dongtai_agent_python.setting import Setting, const
from dongtai_agent_python.utils import scope, utils


@scope.with_scope(scope.SCOPE_AGENT)
def wrap_data(policy_rule, self_obj=None, result=None, come_args=None, come_kwargs=None):
    setting = Setting()
    if setting.is_agent_paused():
        return

    context = CONTEXT_TRACKER.current()
    if not utils.needs_propagation(context, policy_rule.node_type):
        return

    if not filter_result(result, policy_rule.node_type):
        return

    if policy_rule.node_type == const.NODE_TYPE_SOURCE:
        context.has_source = True

    tracking = Tracking(policy_rule)
    tracking.apply(self_obj, result, come_args, come_kwargs)


def filter_result(result, node_type=None):
    if node_type != const.NODE_TYPE_SINK:
        if utils.is_empty(result) or utils.is_not_allowed_type(result):
            return False

    return True
