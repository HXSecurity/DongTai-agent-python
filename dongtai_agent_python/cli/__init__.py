import os
import sys
import time

_builtin_commands = [
    'run',
]

_commands = {}


def command(name, options='', description='', hidden=False,
            log_intercept=True, deprecated=False):
    def wrapper(callback):
        callback.name = name
        callback.options = options
        callback.description = description
        callback.hidden = hidden
        callback.log_intercept = log_intercept
        callback.deprecated = deprecated
        _commands[name] = callback
        return callback

    return wrapper


def usage(name):
    cmd = _commands[name]
    if cmd.deprecated:
        print("Command %s is deprecated" % (name,))
    print('Usage: dongtai-cli %s %s' % (name, cmd.options))


def log_message(text):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print('[%s] [%d] DongTai: %s' % (timestamp, os.getpid(), text))


def load_internal_commands():
    for name in _builtin_commands:
        module_name = '%s.%s' % (__name__, name)
        __import__(module_name)


def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    else:
        print("Command can not empty")
        sys.exit(1)

    try:
        callback = _commands[cmd]
    except Exception:
        print("Unknown command " + cmd)
        sys.exit(1)

    callback(sys.argv[2:])


load_internal_commands()

if __name__ == '__main__':
    main()
