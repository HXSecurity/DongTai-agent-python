import os
import threading

from dongtai_agent_python.setting.config import Config
from dongtai_agent_python.utils.singleton import Singleton


class Setting(Singleton):
    def init(self, container=None):
        self.paused = False
        self.manual_paused = False
        self.request_seq = 0

        self.auto_create_project = 0
        self.use_local_policy = False
        self.os_env_list = []

        self.policy = {}

        self.container = {}
        if container and isinstance(container, dict):
            self.container = container

        self.config = Config()
        self.project_name = self.config.get('project', {}).get('name', 'Demo Project')
        self.project_version = self.config.get('project', {}).get('version', '')
        # engine.name will auto generated when download
        self.engine_name = self.config.get('engine', {}).get('name', 'dongtai-agent-python')
        self.log_path = self.config.get("log", {}).get("log_path", "./dongtai_py_agent.log")

        self.init_os_environ()

    def init_os_environ(self):
        os_env = dict(os.environ)
        if not isinstance(os_env, dict):
            return

        # windows always upper case env key
        project_name = os_env.get('PROJECT_NAME', '') or os_env.get('PROJECTNAME', '') or os_env.get('projectName', '')
        if project_name:
            self.project_name = project_name

        if os_env.get('PROJECT_VERSION', ''):
            self.project_version = os_env.get('PROJECT_VERSION', '')

        if os_env.get('ENGINE_NAME', ''):
            self.engine_name = os_env.get('ENGINE_NAME', '')

        if os_env.get('AUTO_CREATE_PROJECT', '') == '1':
            self.auto_create_project = os_env.get('AUTO_CREATE_PROJECT', '')

        if os_env.get('USE_LOCAL_POLICY', '') == '1':
            self.use_local_policy = True

        if os_env.get('LOG_PATH', ''):
            self.log_path = os_env.get('LOG_PATH', '')

        for key in os_env.keys():
            self.os_env_list.append(key + '=' + str(os_env[key]))

    def is_agent_paused(self):
        return self.paused and self.manual_paused

    def incr_request_seq(self):
        self.request_seq = self.request_seq + 1
