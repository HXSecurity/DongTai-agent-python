import base64
import hashlib

from dongtai_agent_python.common import origin

NODE_TYPE_PROPAGATOR = 1
NODE_TYPE_SOURCE = 2
NODE_TYPE_FILTER = 3
NODE_TYPE_SINK = 4

FIRST_RETURN = [
    'builtins.list.append',
    'builtins.list.insert',
]


def normalize_response_header(status_line, headers):
    header_str = status_line + "\n" + json_to_str(headers)
    header_str = base64.b64encode(header_str.encode('utf-8'))
    header_str = origin.bytes_decode(header_str, 'utf-8')
    return header_str


def json_to_base64(json_data):
    if json_data:
        json_data = json_to_str(json_data)
        json_data = base64.b64encode(json_data.encode('utf-8'))
        json_data = origin.bytes_decode(json_data, 'utf-8')
    return json_data


def bytes_to_base64(data):
    b64_data = base64.b64encode(data)
    return origin.bytes_decode(b64_data, 'utf-8')


def json_to_str(json_data):
    if json_data:
        new_list = []
        for item in json_data.keys():
            origin.list_append(new_list, str(item) + "=" + str(json_data[item]))
        json_data = origin.str_join("\n", new_list)
    return json_data


def is_empty(value):
    if value is None:
        return True
    if isinstance(value, (tuple, list, dict, str, bytes, bytearray)):
        return not value
    return False


def is_not_allowed_type(value):
    return type(value) == int or type(value) == bool


def get_hash(item):
    try:
        h = hashlib.md5((str(type(item)) + ":" + str(id(item)) + ":" + str(item)).encode('utf-8')).hexdigest()
    except Exception:
        h = id(item)
    return h

def recursive_get_hashes(items, hashes=None):
    if hashes is None:
        hashes = []

    for item in items:
        origin.list_append(hashes, get_hash(item))

        if isinstance(item, (tuple, list)):
            hashes = recursive_get_hashes(item, hashes)
        elif isinstance(item, dict):
            hashes = recursive_get_hashes(list(item.values()), hashes)
    return hashes