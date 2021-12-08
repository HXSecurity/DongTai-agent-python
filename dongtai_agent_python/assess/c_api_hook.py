from dongtai_agent_python.policy.deal_data import wrap_data
from dongtai_agent_python.setting import const
from dongtai_agent_python.utils import scope


def callback_unicode_fstring(target, self, result, *args, **kwargs):
    if scope.in_scope(scope.SCOPE_AGENT):
        return
    wrap_data(target, 'str', 'fstring', signature='builtins.str.fstring',
              node_type=const.NODE_TYPE_PROPAGATOR, come_args=args, come_kwargs=kwargs)


def callback_bytes_cformat(target, self, result, *args, **kwargs):
    if scope.in_scope(scope.SCOPE_AGENT):
        return
    wrap_data(target, 'bytes', 'cformat', signature='builtins.bytes.cformat',
              node_type=const.NODE_TYPE_PROPAGATOR, come_args=args, come_kwargs=kwargs)


def callback_bytearray_cformat(target, self, result, *args, **kwargs):
    if scope.in_scope(scope.SCOPE_AGENT):
        return
    wrap_data(target, 'bytearray', 'cformat', signature='builtins.bytearray.cformat',
              node_type=const.NODE_TYPE_PROPAGATOR, come_args=args, come_kwargs=kwargs)


def callback_unicode_cformat(target, self, result, *args, **kwargs):
    if scope.in_scope(scope.SCOPE_AGENT):
        return
    wrap_data(target, 'str', 'cformat', signature='builtins.str.cformat',
              node_type=const.NODE_TYPE_PROPAGATOR, come_args=args, come_kwargs=kwargs)
