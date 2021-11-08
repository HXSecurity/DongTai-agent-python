import time
from concurrent.futures import ThreadPoolExecutor

import dongtai_agent_python.global_var as dt_global_var
from dongtai_agent_python.assess.patch import enable_patches
from dongtai_agent_python.common.logger import logger_config
from dongtai_agent_python.report.upload_data import AgentUpload

logger = logger_config("base_middleware")


class BaseMiddleware(object):
    loaded = False

    def __init__(self, current_middleware):
        if BaseMiddleware.loaded:
            return

        dt_global_var.dt_set_value("dt_open_pool", False)
        self.current_middleware = current_middleware
        if not current_middleware.get("module_name", ""):
            dt_global_var.dt_set_value("dt_open_pool", True)
            return

        logger.info("python agent init")
        start_time = time.time()

        self.executor = ThreadPoolExecutor()
        self.agent_upload = AgentUpload(self.current_middleware)
        # register agent
        register_resp = self.agent_upload.agent_register()
        if register_resp.get("status", 0) == 201:
            dt_agent_id = register_resp.get("data", {}).get("id", 0)
            logger.info("python agent register success ")
        else:
            dt_agent_id = 0
            logger.error("python agent register error ")

        dt_global_var.dt_set_value("agentId", dt_agent_id)
        logger.debug("------begin hook-----")
        enable_patches(self.current_middleware)

        self.agent_upload.report_startup_time((time.time() - start_time) * 1000)
        logger.info("python agent hook open")
        dt_global_var.dt_set_value("dt_open_pool", True)
        BaseMiddleware.loaded = True
