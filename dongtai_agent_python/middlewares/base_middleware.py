import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

from dongtai_agent_python.api import OpenAPI
from dongtai_agent_python.assess.patch import enable_patches
from dongtai_agent_python.common.logger import logger_config
from dongtai_agent_python.setting import Setting
from dongtai_agent_python.utils import scope

logger = logger_config("base_middleware")


class BaseMiddleware(object):
    loaded = False

    def __init__(self, container):
        if BaseMiddleware.loaded:
            return

        logger.info("python agent init")
        start_time = time.time()
        scope.enter_scope(scope.SCOPE_AGENT)

        # middleware id
        self.id = id(self)
        self.setting = None
        self.executor = ThreadPoolExecutor()
        self.init_setting(container)

        self.openapi = OpenAPI(self.setting)

        # register agent
        register_resp = self.openapi.agent_register()
        if register_resp.get("status", 0) == 201:
            logger.info("python agent register success ")
        else:
            logger.error("python agent register error ")

        logger.debug("------begin hook-----")
        policies = self.get_policies()
        enable_patches(policies)

        self.openapi.agent_startup_time((time.time() - start_time) * 1000)
        logger.info("python agent hook open")

        scope.exit_scope()
        BaseMiddleware.loaded = True

    def init_setting(self, container):
        self.setting = Setting(container)

    def get_policies(self):
        if self.setting.use_local_policy:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_dir, '../policy_api.json')
            with open(file_path, 'r') as f:
                policies = json.load(f)
        else:
            policies = self.openapi.get_policies()

        if policies.get("status", 0) != 201:
            return []
        return policies.get('data', [])
