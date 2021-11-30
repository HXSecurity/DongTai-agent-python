import base64
import decimal
import gzip
import json
import os
import platform
import traceback

import requests
import socket
import threading
from dongtai_agent_python.common.logger import logger_config
from dongtai_agent_python.utils import scope
from dongtai_agent_python.utils import Singleton, SystemInfo

logger = logger_config('openapi')


class OpenAPI(Singleton):
    def __init__(self, setting):
        self.setting = setting
        self.config = setting.config
        self.base_url = self.config.get('iast', {}).get('server', {}).get('url', '')
        self.interval = self.config.get('iast', {}).get('service', {}).get('report', {}).get('interval', 5)
        self.interval_check_enable = 60
        self.interval_check_manual_pause = 5

        self.agent_id = 0
        self.report_queue = 0
        self.session = requests.session()

        self.headers = {
            'Authorization': 'Token ' + self.config.get('iast', {}).get('server', {}).get('token', ''),
            'user-agent': 'DongTaiIAST-Agent',
            'content-encoding': 'gzip',
            'content-type': 'application/json'
        }

        agent_prefix = platform.system() + ' ' + platform.release() + '-' + socket.gethostname()
        self.agent_version = self.config.get('engine', {}).get('version', 'v1.0.0')
        self.agent_name = agent_prefix + '-' + self.agent_version + '-' + self.setting.engine_name

        self.system_info = SystemInfo()

    @scope.with_scope(scope.SCOPE_AGENT)
    def get(self, url, params=None):
        full_url = self.base_url + url

        try:
            res = self.session.get(full_url, timeout=20, headers=self.headers, params=params)
            resp = bytes.decode(res.content, 'utf-8')
            resp = json.loads(resp)
        except Exception as e:
            logger.error("get " + url + " failed: " + str(e) + "\n" + traceback.format_exc())
            resp = {}

        return resp

    @scope.with_scope(scope.SCOPE_AGENT)
    def post(self, url, body):
        full_url = self.base_url + url

        try:
            body_data = json.dumps(body)
            res = self.session.post(full_url, timeout=20, headers=self.headers, data=body_data)
            resp = bytes.decode(res.content, 'utf-8')
            resp = json.loads(resp)
        except Exception as e:
            logger.error("post " + url + " failed: " + str(e) + "\n" + traceback.format_exc())
            resp = {}

        return resp

    @scope.with_scope(scope.SCOPE_AGENT)
    def report(self, url, body):
        api_url = self.base_url + url
        logger.debug(body)
        stream_data = json.dumps(body)

        body_data = gzip.compress(stream_data.encode('utf-8'))
        try:
            res = self.session.post(api_url, data=body_data, timeout=20, headers=self.headers)
            logger.debug(res.content)
            resp = bytes.decode(res.content, 'utf-8')
            resp = json.loads(resp)
        except Exception as e:
            logger.error("report failed: " + str(e) + "\n" + traceback.format_exc())
            resp = {}

        return resp

    def get_policies(self):
        url = '/api/v1/profiles?language=PYTHON'
        resp = self.get(url)

        return resp

    @scope.with_scope(scope.SCOPE_AGENT)
    def thread_heart_report(self):
        # 上报心跳数据
        system_info = {
            'detail': {
                # 'disk': origin.json_dumps(self.cur_system_info.get_disk()),
                'memory': json.dumps(self.system_info.get_memory_info()),
                'agentId': self.agent_id,
                'cpu': json.dumps({'rate': self.system_info.get_cpu_rate()}),
                'methodQueue': 0,
                'replayQueue': 0,
                'reqCount': self.setting.request_seq,
                'reportQueue': self.report_queue
            },
            'type': 1
        }
        url = '/api/v1/report/upload'
        heart_resp = self.report(url, system_info)
        if heart_resp.get('status', 0) == 201:
            logger.debug("report heart data success")
        else:
            logger.error("report heart data error")

        t1 = threading.Timer(self.interval, self.thread_heart_report)
        t1.start()

    def thread_check_enable(self):
        is_paused = self.setting.paused
        if not self.check_enable():
            if not is_paused:
                logger.info("resource limit: agent pause")
                self.setting.paused = True
        else:
            if is_paused:
                logger.info("resource limit: agent unpause")
                self.setting.paused = False

        t1 = threading.Timer(self.interval_check_enable, self.thread_check_enable)
        t1.start()

    def thread_check_manual_pause(self):
        is_paused = self.setting.manual_paused
        resp = self.check_manual_pause()
        if resp == 'coreStop':
            if not is_paused:
                logger.info("agent manual pause")
                self.setting.manual_paused = True
        elif resp == 'coreStart' or resp == 'coreRegisterStart':
            if is_paused:
                logger.info("agent manual unpause: " + resp)
                self.setting.manual_paused = False

        t1 = threading.Timer(self.interval_check_manual_pause, self.thread_check_manual_pause)
        t1.start()

    @scope.with_scope(scope.SCOPE_AGENT)
    def agent_register(self):
        url = '/api/v1/agent/register'

        env_str = ','.join(self.setting.os_env_list)
        server_env_str = base64.b64encode(env_str.encode('utf-8'))
        network_info = self.system_info.print_net_if_addr()
        register_data = {
            'name': self.agent_name,
            'language': 'PYTHON',
            'version': self.agent_version,
            'projectName': self.setting.project_name,
            'hostname': socket.gethostname(),
            'network': network_info,
            'containerName': self.setting.container.get('name', ''),
            'containerVersion': self.setting.container.get('version', ''),
            'serverAddr': '',
            'serverPort': '',
            'serverPath': '',
            'serverEnv': server_env_str.decode('utf-8'),
            'pid': str(os.getpid()),
            'autoCreateProject': self.setting.auto_create_project,
        }
        if self.setting.project_version != '':
            register_data['projectVersion'] = self.setting.project_version
        resp = self.report(url, register_data)
        if resp.get('status', 0) != 201:
            return resp

        self.setting.agent_id = self.agent_id = resp.get('data', {}).get('id', 0)
        if not self.agent_id:
            logger.error("register get agent id empty")
            return resp

        if resp.get('data', {}).get('coreAutoStart', 0) != 1:
            logger.info("agent is waiting for auditing")
            self.setting.dt_manual_pause = True

        if self.setting.disable_heartbeat:
            return resp

        # heartbeat thread
        t1 = threading.Timer(self.interval, self.thread_heart_report)
        t1.start()
        # check enable thread
        t2 = threading.Timer(self.interval_check_enable, self.thread_check_enable)
        t2.start()
        # check manual pause
        t3 = threading.Timer(self.interval_check_manual_pause, self.thread_check_manual_pause)
        t3.start()

        return resp

    def report_upload(self, upload_report):
        url = '/api/v1/report/upload'
        resp = self.report(url, upload_report)
        self.report_queue = self.report_queue - 1

        return resp

    def async_report_upload(self, executor, upload_report):
        self.report_queue = self.report_queue + 1
        executor.submit(self.report_upload, upload_report)

    # check agent should pause when use high system resource
    def check_enable(self):
        url = '/api/v1/agent/limit'
        resp = self.get(url)
        if resp.get('status', 0) != 201:
            return True

        limits = resp.get('data', [])
        if len(limits) == 0:
            return True
        for limit in limits:
            if limit.get('key', '') == 'cpu_limit':
                cpu_limit = decimal.Decimal(limit.get('value', 0))
                if cpu_limit <= 0:
                    return True
                current_cpu = decimal.Decimal(self.system_info.get_cpu_rate())
                if current_cpu >= cpu_limit:
                    return False

        return True

    def check_manual_pause(self):
        url = '/api/v1/engine/action'
        resp = self.get(url, {
            'agentId': self.agent_id
        })

        # notcmd: no handling
        return resp.get('data', '')

    def agent_startup_time(self, start_time):
        url = '/api/v1/agent/startuptime'
        data = {
            'agentId': self.agent_id,
            'startupTime': int(start_time)
        }
        resp = self.post(url, data)
        if resp.get('status', 0) == 201:
            logger.info("startup time: " + str(start_time) + "ms")
        else:
            logger.info("startup time: " + str(start_time) + "ms report failed")
        return resp
