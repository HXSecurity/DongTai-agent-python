import sys

from dongtai_agent_python.policy.deal_data import wrap_data
from dongtai_agent_python.setting import const
from dongtai_agent_python.utils import scope


# 普通方法 hook
class BuildFuncPatch(object):
    def __init__(self, origin_method, policy_rule):
        self.policy_rule = policy_rule
        self.policy_rule.set_origin_method(origin_method)
        self.policy_rule.set_patched_method(self)

        self.__name__ = origin_method.__name__

    def __call__(self, *args, **kwargs):
        if self.policy_rule.node_type == const.NODE_TYPE_FILTER:
            with scope.scope(scope.SCOPE_AGENT):
                result = self.policy_rule.origin_method(*args, **kwargs)
        else:
            result = self.policy_rule.origin_method(*args, **kwargs)

        if scope.in_scope(scope.SCOPE_AGENT):
            return result

        wrap_data(self.policy_rule, result=result, come_args=args, come_kwargs=kwargs)

        return result


def build_exec_eval_patch(origin_method, policy_rule):
    policy_rule.set_origin_method(origin_method)

    def exec_eval_patch(code, globs=None, locs=None):
        """
        Code ported from six module
        @see: https://github.com/benjaminp/six/blob/45f1a230f9cc8e48372e19627b91ac06a2013292/six.py#L725
        """

        if globs is None:
            frame = sys._getframe(1)

            globs = frame.f_globals
            if locs is None:
                locs = frame.f_locals
            del frame
        elif locs is None:
            locs = globs

        try:
            with scope.scope(scope.SCOPE_AGENT):
                result = origin_method(code, globs, locs)
        except Exception:
            raise

        if scope.in_scope(scope.SCOPE_AGENT):
            return result

        wrap_data(policy_rule, result=result, come_args=[code])

        return result

    policy_rule.set_patched_method(exec_eval_patch)

    return exec_eval_patch
