import re

CONTAINER_DJANGO = 'Django'
CONTAINER_FLASK = 'Flask'

NODE_TYPE_PROPAGATOR = 1
NODE_TYPE_SOURCE = 2
NODE_TYPE_FILTER = 3
NODE_TYPE_SINK = 4

NODE_TYPES = [
    NODE_TYPE_PROPAGATOR,
    NODE_TYPE_SOURCE,
    NODE_TYPE_FILTER,
    NODE_TYPE_SINK,
]

TAINT_SOURCE = 1
TAINT_TARGET = 2

EMPTY_PATTERN = type(re.compile(''))

C_API_PATCHES = [
    'builtins.str.fstring',
    'builtins.str.cformat',
    'builtins.bytes.cformat',
    'builtins.bytearray.cformat',
    'builtins.str.__new__',
    'builtins.bytes.__new__',
    'builtins.bytearray.__init__',
    'builtins.str.__add__',
    'builtins.bytes.__add__',
    'builtins.bytearray.__add__',
]

CRYPTO_BAD_CIPHER_NEW = [
    'Crypto.Cipher.Blowfish.new',
    'Crypto.Cipher.DES.new',
    'Cryptodome.Cipher.Blowfish.new',
    'Cryptodome.Cipher.DES.new',
]

RESPONSE_SIGNATURES = [
    'django.http.response.HttpResponse.__init__',
]
