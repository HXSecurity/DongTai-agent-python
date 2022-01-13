import sys

from dongtai_agent_python.policy.deal_data import wrap_data
from dongtai_agent_python.setting import const
from dongtai_agent_python.utils import scope


# 普通方法 hook
class InstallFcnHook(object):
    def __init__(self, origin_cls, origin_func, signature=None, node_type=None):
        self.signature = signature
        self.origin_func = origin_func
        self.__name__ = origin_func.__name__

        self.origin_cls = origin_cls
        self.node_type = node_type

    def __call__(self, *args, **kwargs):
        if self.node_type == const.NODE_TYPE_FILTER:
            with scope.scope(scope.SCOPE_AGENT):
                result = self.origin_func(*args, **kwargs)
        else:
            result = self.origin_func(*args, **kwargs)

        if scope.in_scope(scope.SCOPE_AGENT):
            return result

        wrap_data(
            result, self.origin_cls.__name__, self.origin_func.__name__,
            signature=self.signature, node_type=self.node_type,
            come_args=args, come_kwargs=kwargs)

        return result


def build_exec_eval_patch(origin_cls, origin_func, signature, node_type):
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
                result = origin_func(code, globs, locs)
        except Exception:
            raise

        if scope.in_scope(scope.SCOPE_AGENT):
            return result

        wrap_data(
            result, origin_cls.__name__, origin_func.__name__,
            signature=signature, node_type=node_type,
            come_args=[code])

        return result

    return exec_eval_patch
