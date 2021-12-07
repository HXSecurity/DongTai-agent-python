from dongtai_agent_python.utils import scope


@scope.scope(scope.SCOPE_AGENT)
def callback_unicode_fstring(target, self, result, *args, **kwargs):
    # @TODO: processing taint data
    pass


@scope.scope(scope.SCOPE_AGENT)
def callback_bytes_cformat(target, self, result, *args, **kwargs):
    return callback_cformat(target, self, result, *args, **kwargs)


@scope.scope(scope.SCOPE_AGENT)
def callback_bytearray_cformat(target, self, result, *args, **kwargs):
    return callback_cformat(target, self, result, *args, **kwargs)


@scope.scope(scope.SCOPE_AGENT)
def callback_unicode_cformat(target, self, result, *args, **kwargs):
    return callback_cformat(target, self, result, *args, **kwargs)


def callback_cformat(target, self, result, *args, **kwargs):
    # @TODO: processing taint data
    pass
