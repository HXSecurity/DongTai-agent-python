import sys

from dongtai_agent_python.policy.deal_data import wrap_data
from dongtai_agent_python.utils import scope

module = sys.modules[__name__]

CALLBACK_NAMES = {
    'builtins.bytes.__new__': 'callback_bytes_cast',
    'builtins.bytearray.__init__': 'callback_bytearray_cast',
    'builtins.str.__new__': 'callback_unicode_cast',
    'builtins.bytes.__add__': 'callback_bytes_concat',
    'builtins.bytearray.__add__': 'callback_bytearray_concat',
    'builtins.str.__add__': 'callback_unicode_concat',
}


def callback_propagator(policy_rule):
    def propagate(target, self_obj, result, args, kwargs):
        if scope.in_scope(scope.SCOPE_AGENT):
            return
        wrap_data(policy_rule, self_obj=self_obj, result=result, come_args=args, come_kwargs=kwargs)

    return propagate


@scope.with_scope(scope.SCOPE_AGENT)
def build_callback_function(policy_rule):
    if policy_rule.signature in CALLBACK_NAMES:
        callback_name = CALLBACK_NAMES[policy_rule.signature]
    else:
        callback_class_name = policy_rule.class_name
        if callback_class_name == 'str':
            callback_class_name = 'unicode'
        callback_name = "callback_{}_{}".format(callback_class_name, policy_rule.method_name)
    callback = callback_propagator(policy_rule)
    callback.__name__ = callback_name
    setattr(module, callback_name, callback)
