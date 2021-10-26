import logging
import dongtai_agent_python.global_var as dt_global_var

loggers = {}

LOG_FORMAT = '[%(asctime)s] %(levelname)s [%(name)s] %(message)s'  # 每条日志输出格式


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
    config_data = dt_global_var.dt_get_value("config_data")
    log_path = config_data.get("log",{}).get("log_path", "./dongtai_py_agent_log.txt")

    logger = logging.getLogger(logging_name)
    logger.handlers.clear()

    if config_data.get("debug"):
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
    return logger
