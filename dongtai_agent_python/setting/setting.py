import os

from dongtai_agent_python import version
from .config import Config
from dongtai_agent_python.utils import Singleton


class Setting(Singleton):
    loaded = False

    def init(self):
        if Setting.loaded:
            return

        self.version = version.__version__
        self.paused = False
        self.manual_paused = False
        self.agent_id = 0
        self.request_seq = 0

        self.auto_create_project = 0
        self.use_local_policy = False
        self.disable_heartbeat = False
        self.os_env_list = []

        self.policy = {}

        self.container = {}

        self.config = Config()
        self.debug = self.config.get("debug", False)
        self.project_name = self.config.get('project', {}).get('name', 'Demo Project')
        self.project_version = self.config.get('project', {}).get('version', '')
        # engine.name will auto generated when download
        self.engine_name = self.config.get('engine', {}).get('name', 'dongtai-agent-python')
        self.log_path = self.config.get("log", {}).get("log_path", "./dongtai_py_agent.log")

        self.init_os_environ()
        Setting.loaded = True

    def set_container(self, container):
        if container and isinstance(container, dict):
            self.container = container

    def init_os_environ(self):
        os_env = dict(os.environ)
        if not isinstance(os_env, dict):
            return

        if os_env.get('DEBUG', '') == '1':
            self.debug = True

        # windows always upper case env key
        project_name = os_env.get('PROJECT_NAME', '') or os_env.get('PROJECTNAME', '') or os_env.get('projectName', '')
        if project_name:
            self.project_name = project_name

        if os_env.get('PROJECT_VERSION', ''):
            self.project_version = os_env.get('PROJECT_VERSION', '')

        if os_env.get('ENGINE_NAME', ''):
            self.engine_name = os_env.get('ENGINE_NAME', '')

        if os_env.get('AUTO_CREATE_PROJECT', '') == '1':
            self.auto_create_project = 1

        if os_env.get('USE_LOCAL_POLICY', '') == '1':
            self.use_local_policy = True

        if os_env.get('DISABLE_HEARTBEAT', '') == '1':
            self.disable_heartbeat = True

        if os_env.get('LOG_PATH', ''):
            self.log_path = os_env.get('LOG_PATH', '')

        for key in os_env.keys():
            self.os_env_list.append(key + '=' + str(os_env[key]))

    def is_agent_paused(self):
        return self.paused and self.manual_paused

    def incr_request_seq(self):
        self.request_seq = self.request_seq + 1
