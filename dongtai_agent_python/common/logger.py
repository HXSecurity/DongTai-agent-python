import logging
from dongtai_agent_python.setting import Setting
from dongtai_agent_python.utils import scope

loggers = {}

LOG_FORMAT = '[%(asctime)s] %(levelname)s [%(name)s] %(message)s'  # 每条日志输出格式


class AgentLogger(object):
    def __init__(self, log):
        self._log = log

    @scope.with_scope(scope.SCOPE_AGENT)
    def debug(self, msg, *args, **kwargs):
        return self._log.debug(msg, *args, **kwargs)

    @scope.with_scope(scope.SCOPE_AGENT)
    def info(self, msg, *args, **kwargs):
        return self._log.info(msg, *args, **kwargs)

    @scope.with_scope(scope.SCOPE_AGENT)
    def warning(self, msg, *args, **kwargs):
        return self._log.warning(msg, *args, **kwargs)

    @scope.with_scope(scope.SCOPE_AGENT)
    def warn(self, msg, *args, **kwargs):
        return self._log.warn(msg, *args, **kwargs)

    @scope.with_scope(scope.SCOPE_AGENT)
    def error(self, msg, *args, **kwargs):
        return self._log.error(msg, *args, **kwargs)

    @scope.with_scope(scope.SCOPE_AGENT)
    def exception(self, msg, *args, exc_info=True, **kwargs):
        return self._log.exception(msg, *args, exc_info, **kwargs)

    @scope.with_scope(scope.SCOPE_AGENT)
    def critical(self, msg, *args, **kwargs):
        return self._log.critical(msg, *args, **kwargs)

    @scope.with_scope(scope.SCOPE_AGENT)
    def log(self, level, msg, *args, **kwargs):
        return self._log.log(level, msg, *args, **kwargs)


@scope.with_scope(scope.SCOPE_AGENT)
def logger_config(logging_name):
    """
    get logger by name
    :param logging_name: name of logger
    :return: logger
    """

    global loggers

    if loggers.get(logging_name):
        return loggers.get(logging_name)

    # get config
    setting = Setting()
    log_path = setting.log_path

    logger = logging.getLogger(logging_name)
    logger.handlers.clear()

    if setting.config.get("debug"):
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger.setLevel(level)

    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console)

    loggers[logging_name] = logger
    return AgentLogger(logger)
