import sys

from dongtai_agent_python import CONTEXT_TRACKER
from dongtai_agent_python.policy.deal_data import wrap_data
from dongtai_agent_python.setting import Setting
from dongtai_agent_python.utils import scope, utils


# 普通方法 hook
class InstallFcnHook(object):
    def __init__(self, old_cls, fcn, signature=None, node_type=None):
        self.signature = signature
        self._fcn = fcn
        self.__name__ = fcn.__name__

        self.old_cls = old_cls
        self.node_type = node_type

    def __call__(self, *args, **kwargs):
        ret_val = self._fcn(*args, **kwargs)

        if scope.in_scope(scope.SCOPE_AGENT):
            return ret_val

        context = CONTEXT_TRACKER.current()
        if not utils.needs_propagation(context, self.node_type):
            return ret_val

        with scope.scope(scope.SCOPE_AGENT):
            setting = Setting()
        if setting.is_agent_paused():
            return ret_val

        wrap_data(
            ret_val, self.old_cls.__name__, self._fcn,
            signature=self.signature, node_type=self.node_type,
            come_args=args, come_kwargs=kwargs,
            extra_in=None, real_result=ret_val)

        return ret_val


def build_exec_eval_patch(orig_cls, orig_func, signature, node_type):
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
                ret_val = orig_func(code, globs, locs)
        except Exception:
            ret_val = None
            raise

        if scope.in_scope(scope.SCOPE_AGENT):
            return ret_val

        context = CONTEXT_TRACKER.current()
        if not utils.needs_propagation(context, node_type):
            return ret_val

        with scope.scope(scope.SCOPE_AGENT):
            setting = Setting()
        if setting.is_agent_paused():
            return ret_val

        wrap_data(
            ret_val, orig_cls.__name__, orig_func,
            signature=signature, node_type=node_type,
            come_args=[code], real_result=ret_val)
        return ret_val

    return exec_eval_patch
