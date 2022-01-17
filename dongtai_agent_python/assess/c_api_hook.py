from dongtai_agent_python.policy.deal_data import wrap_data
from dongtai_agent_python.setting import const
from dongtai_agent_python.utils import scope


def callback_propagator(target, origin_cls, origin_func, signature, args=None, kwargs=None):
    if scope.in_scope(scope.SCOPE_AGENT):
        return
    wrap_data(target, origin_cls, origin_func, signature=signature,
              node_type=const.NODE_TYPE_PROPAGATOR, come_args=args, come_kwargs=kwargs)


def callback_unicode_fstring(target, self, result, args, kwargs):
    callback_propagator(target, 'str', 'fstring', signature='builtins.str.fstring', args=args, kwargs=kwargs)


def callback_bytes_cformat(target, self, result, args, kwargs):
    callback_propagator(target, 'bytes', 'cformat', signature='builtins.bytes.cformat', args=args, kwargs=kwargs)


def callback_bytearray_cformat(target, self, result, args, kwargs):
    callback_propagator(target, 'bytearray', 'cformat', signature='builtins.bytearray.cformat', args=args, kwargs=kwargs)


def callback_unicode_cformat(target, self, result, args, kwargs):
    callback_propagator(target, 'str', 'cformat', signature='builtins.str.cformat', args=args, kwargs=kwargs)


def callback_bytes_cast(target, self, result, args, kwargs):
    callback_propagator(target, 'bytes', '__new__', signature='builtins.bytes.__new__', args=args, kwargs=kwargs)


def callback_bytearray_cast(target, self, result, args, kwargs):
    callback_propagator(target, 'bytearray', '__init__', signature='builtins.bytearray.__init__', args=args, kwargs=kwargs)


def callback_unicode_cast(target, self, result, args, kwargs):
    callback_propagator(target, 'str', '__new__', signature='builtins.str.__new__', args=args, kwargs=kwargs)
