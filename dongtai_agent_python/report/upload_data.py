import base64
import decimal
import gzip
import os
import platform
import requests
import socket
import threading
import traceback

import dongtai_agent_python.global_var as dt_global_var
from dongtai_agent_python.common import origin
from dongtai_agent_python.common.logger import logger_config

logger = logger_config("upload_data")


# 获取系统信息
class SystemInfo(object):
    def __init__(self):
        self.unit = 1024 * 1024 * 1024
        try:
            import psutil
            self.psutil = psutil
            logger.info("psutil import success")
        except Exception as e:
            self.psutil = None
            logger.error("psutil import error, please pip3 install psutil")

    # 获取网络信息
    def print_net_if_addr(self):
        if self.psutil is not None:
            try:
                dic = self.psutil.net_if_addrs()
                network_arr = []
                for adapter in dic:
                    snic_list = dic[adapter]
                    mac = '无 mac 地址'
                    ipv4 = '无 ipv4 地址'
                    ipv6 = '无 ipv6 地址'
                    for snic in snic_list:
                        if snic.family.name in {'AF_LINK', 'AF_PACKET'}:
                            mac = snic.address
                        elif snic.family.name == 'AF_INET':
                            ipv4 = snic.address
                        elif snic.family.name == 'AF_INET6':
                            ipv6 = snic.address
                    origin.list_append(network_arr, '%s, %s, %s, %s' % (adapter, mac, ipv4, ipv6))
                logger.info("get network success")
                return origin.str_join(";", network_arr)
            except Exception as e:
                logger.error("get network" + str(e))
                return ""
        else:
            return ""

    # 获取cpu信息
    def get_cpu_rate(self):
        if self.psutil is not None:
            # print(self.psutil.cpu_percent())
            percent = self.psutil.cpu_percent()
            return percent
        else:
            return 0

    # 获取系统内存使用情况
    def get_memory_info(self):
        if self.psutil is not None:
            memory_info = self.psutil.virtual_memory()
            return {
                "total": round(memory_info.total / self.unit, 2),
                "used": round(memory_info.used / self.unit, 2),
                "rate": memory_info.percent
            }
        else:
            return {
                "total": 0,
                "use": 0,
                "rate": 0
            }

    # 获取磁盘信息
    def get_disk(self):
        disk = {"info": []}
        if self.psutil is not None:
            devs = self.psutil.disk_partitions()
            if devs:
                for dev in devs:
                    diskinfo = self.psutil.disk_usage(dev.mountpoint)
                    # 将字节转换成G
                    origin.list_append(disk['info'], {
                        "name": dev.device,
                        "total": str(round(diskinfo.total / self.unit, 2)) + "G",
                        "used": str(round(diskinfo.used / self.unit, 2)) + "G",
                        "free": str(round(diskinfo.free / self.unit, 2)) + "G",
                        "rate": str(diskinfo.percent) + "%",
                        "fstype": dev.fstype
                    })
        return disk


class AgentUpload(object):

    def __init__(self, current_middleware):
        self.current_middleware = current_middleware
        self.pending_report = 0
        self.session = requests.session()
        self.config_data = dt_global_var.dt_get_value("config_data")
        self.dt_agent_id = 0
        self.iast_url = self.config_data.get("iast", {}).get("server", {}).get("url", "")
        self.interval = self.config_data.get("iast", {}).get("service", {}).get("report", {}).get("interval", 5)
        self.interval_check_enable = 60
        self.interval_check_manual_pause = 5
        self.cur_system_info = {}
        self.headers = {
            "Authorization": "Token " + self.config_data.get("iast", {}).get("server", {}).get("token", ""),
            "user-agent": "DongTaiIAST-Agent",
            'content-encoding': 'gzip',
            'content-type': "application/json"
        }

        agent_prefix = platform.system() + " " + platform.release() + "-" + socket.gethostname()
        self.agent_version = self.config_data.get("engine", {}).get("version", "v1.0.0")
        # engine.name will auto generated when download
        engine_name = self.config_data.get("engine", {}).get("name", "dongtai-agent-python")
        self.agent_name = agent_prefix + "-" + self.agent_version + "-" + engine_name + "-" + \
                          self.current_middleware.get("container_name", "")

        self.cur_system_info = SystemInfo()

    # 获取接口信息
    def base_api_get(self, url, params=None):
        endpoint = url
        url = self.iast_url + url
        try:
            res = origin.request_session_get(self.session, url, timeout=20, headers=self.headers, params=params)
            resp = res.content.decode("utf-8")
            resp = origin.json_loads(resp)

            # logger.info("report base data")
        except Exception as e:
            logger.error("get  " + endpoint + " data error: " + str(e) + traceback.format_exc())
            resp = {}

        return resp

    def base_api_post(self, url, body_data):
        endpoint = url
        url = self.iast_url + url
        try:
            body_data = origin.json_dumps(body_data)
            res = origin.request_session_post(self.session, url, timeout=20, headers=self.headers, data=body_data)
            resp = res.content.decode("utf-8")
            resp = origin.json_loads(resp)
            # logger.info("report base data")
        except Exception as e:
            logger.error("post " + endpoint + " data error: " + str(e) + traceback.format_exc())
            resp = {}

        return resp

    def base_report(self, url, body):
        url = self.iast_url + url
        logger.debug(body)
        stream_data = origin.json_dumps(body)

        body_data = gzip.compress(stream_data.encode('utf-8'))
        try:
            res = origin.request_session_post(self.session, url, data=body_data, timeout=20, headers=self.headers)
            logger.debug(res.content)
            resp = res.content.decode("utf-8")
            resp = origin.json_loads(resp)

        except Exception as e:
            logger.error("report data error: " + str(e) + traceback.format_exc())
            resp = {}

        return resp

    def thread_heart_report(self):
        # 上报心跳数据
        system_info = {
            "detail": {
                # "disk": origin.json_dumps(self.cur_system_info.get_disk()),
                "memory": origin.json_dumps(self.cur_system_info.get_memory_info()),
                "agentId": self.dt_agent_id,
                "cpu": origin.json_dumps({"rate": self.cur_system_info.get_cpu_rate()}),
                "methodQueue": 0,
                "replayQueue": 0,
                "reqCount": dt_global_var.dt_get_value("req_count"),
                "reportQueue": self.pending_report
            },
            "type": 1
        }
        url = "/api/v1/report/upload"
        heart_resp = self.base_report(url, system_info)
        if heart_resp.get("status", 0) == 201:
            logger.debug("report heart data success")
        else:
            logger.error("report heart data error")

        t1 = threading.Timer(self.interval, self.thread_heart_report)
        t1.start()

    def thread_check_enable(self):
        is_paused = dt_global_var.dt_get_value("dt_pause")
        if not self.check_enable():
            if not is_paused:
                logger.info("resource limit: agent pause")
                dt_global_var.dt_set_value("dt_pause", True)
        else:
            if is_paused:
                logger.info("resource limit: agent unpause")
                dt_global_var.dt_set_value("dt_pause", False)

        t1 = threading.Timer(self.interval_check_enable, self.thread_check_enable)
        t1.start()

    def thread_check_manual_pause(self):
        is_paused = dt_global_var.dt_get_value("dt_manual_pause")
        resp = self.check_manual_pause()
        if resp == "coreStop":
            if not is_paused:
                logger.info("agent manual pause")
                dt_global_var.dt_set_value("dt_manual_pause", True)
        elif resp == "coreStart" or resp == "coreRegisterStart":
            if is_paused:
                logger.info("agent manual unpause: " + resp)
                dt_global_var.dt_set_value("dt_manual_pause", False)

        t1 = threading.Timer(self.interval_check_manual_pause, self.thread_check_manual_pause)
        t1.start()

    def agent_register(self):

        url = "/api/v1/agent/register"
        data = self.current_middleware

        server_env = dict(os.environ)
        server_env_arr = []
        auto_create_project = 0
        project_name = self.config_data.get("project", {}).get("name", "Demo Project")
        if isinstance(server_env, dict):
            if server_env.get("projectName", ""):
                project_name = server_env.get("projectName", "")
            elif server_env.get("PROJECTNAME", ""):
                # windows always upper case env key
                project_name = server_env.get("PROJECTNAME", "")

            if server_env.get("AUTO_CREATE_PROJECT", "") == "1":
                auto_create_project = 1

            for key in server_env.keys():
                origin.list_append(server_env_arr, key + "=" + str(server_env[key]))

        env_str = origin.str_join(",", server_env_arr)

        server_env_str = base64.b64encode(env_str.encode('utf-8'))
        network_info = self.cur_system_info.print_net_if_addr()
        register_data = {
            "name": self.agent_name,
            "language": "PYTHON",
            "version": self.agent_version,
            "projectName": project_name,
            "hostname": socket.gethostname(),
            "network": network_info,
            "containerName": data.get("container_name", ""),
            "containerVersion": data.get("container_version", ""),
            "serverAddr": "",
            "serverPort": "",
            "serverPath": "",
            "serverEnv": server_env_str.decode('utf-8'),
            "pid": str(os.getpid()),
            "autoCreateProject": auto_create_project,
        }
        resp = self.base_report(url, register_data)
        if resp.get("status", 0) != 201:
            return resp

        self.dt_agent_id = resp.get("data", {}).get("id", 0)
        if not self.dt_agent_id:
            logger.error('register get agent id empty')
            return resp

        if resp.get("data", {}).get("coreAutoStart", 0) != 1:
            logger.info("agent is waiting for auditing")
            dt_global_var.dt_set_value("dt_manual_pause", True)

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

    def agent_upload_report(self, upload_report):
        url = "/api/v1/report/upload"
        resp = self.base_report(url, upload_report)
        self.pending_report = self.pending_report - 1

        return resp

    def async_agent_upload_report(self, executor, upload_report):
        self.pending_report = self.pending_report + 1
        executor.submit(self.agent_upload_report, upload_report)

    def get_policy_config(self):

        url = "/api/v1/profiles?language=PYTHON"
        resp = self.base_api_get(url)

        return resp

    # check agent should pause when use high system resource
    def check_enable(self):
        url = "/api/v1/agent/limit"
        resp = self.base_api_get(url)
        if resp.get("status", 0) != 201:
            return True

        limits = resp.get("data", [])
        if len(limits) == 0:
            return True
        for limit in limits:
            if limit.get("key", "") == "cpu_limit":
                cpu_limit = decimal.Decimal(limit.get("value", 0))
                if cpu_limit <= 0:
                    return True
                current_cpu = decimal.Decimal(self.cur_system_info.get_cpu_rate())
                if current_cpu >= cpu_limit:
                    return False

        return True

    def check_manual_pause(self):
        url = "/api/v1/engine/action"
        resp = self.base_api_get(url, {
            "agentId": self.dt_agent_id
        })

        # notcmd: no handling
        return resp.get("data", "")

    def report_startup_time(self, start_time):
        url = "/api/v1/agent/startuptime"
        data = {
            "agentId": self.dt_agent_id,
            "startupTime": int(start_time)
        }
        resp = self.base_api_post(url, data)
        if resp.get("status", 0) == 201:
            logger.info("startup time: " + str(start_time) + "ms")
        else:
            logger.info("startup time: " + str(start_time) + "ms report failed")
        return resp
