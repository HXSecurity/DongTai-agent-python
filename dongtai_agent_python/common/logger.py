import logging, os
import dongtai_agent_python.global_var as dt_global_var


def logger_config(logging_name):
    '''
        logger是日志对象，handler是流处理器，console是控制台输出（没有console也可以，将不会在控制台输出，会在日志文件中输出）
    '''
    # 获取配置信息

    config_data = dt_global_var.dt_get_value("config_data")
    log_path = config_data.get("log",{}).get("log_path", "./dongtai_py_agent_log.txt")

    # 获取logger对象,取名
    logger = logging.getLogger(logging_name)
    # 输出DEBUG及以上级别的信息，针对所有输出的第一层过滤
    logger.setLevel(level=logging.DEBUG)
    # 获取文件日志句柄并设置日志级别，第二层过滤
    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(logging.INFO)
    # 生成并设置文件日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # console相当于控制台输出，handler文件输出。获取流句柄并设置日志级别，第二层过滤
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # 为logger对象添加句柄

    logger.addHandler(console)
    return logger


# if __name__ == "__main__":
#     logger = logger_config(logging_name='据说名字长一点容易被人记住')
#     logger.info("info")
#     logger.error("error")
#     logger.debug("debug")
#     logger.warning("warning")