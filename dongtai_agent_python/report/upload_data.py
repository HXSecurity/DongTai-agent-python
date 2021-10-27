import base64
import gzip
import json
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

    def __init__(self):
        self.pending_report = 0
        self.session = requests.session()
        self.config_data = dt_global_var.dt_get_value("config_data")
        self.dt_agent_id = 0
        self.interval = self.config_data.get("iast", {}).get("service", {}).get("report", {}).get("interval", 30)
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
        self.agent_name = agent_prefix + "-" + self.agent_version + "-" + engine_name

        self.cur_system_info = SystemInfo()

    # 获取接口信息
    def base_api_get(self, url):
        url = self.config_data.get("iast", {}).get("server", {}).get("url", "") + url
        try:
            res = requests.get(url, timeout=20, headers=self.headers)
            resp = res.content.decode("utf-8")
            resp = json.loads(resp)

            # logger.info("report base data")
        except Exception as e:
            logger.error("get data error: " + str(e) + traceback.format_exc())
            resp = {}

        return resp

    def base_report(self, url, body):
        url = self.config_data.get("iast", {}).get("server", {}).get("url", "") + url
        logger.debug(body)
        stream_data = json.dumps(body)

        body_data = gzip.compress(stream_data.encode('utf-8'))
        try:
            res = self.session.post(url, data=body_data, timeout=20, headers=self.headers)
            logger.debug(res.content)
            resp = res.content.decode("utf-8")
            resp = json.loads(resp)

            # logger.info("report base data")
        except Exception as e:
            logger.error("post data error: " + str(e) + traceback.format_exc())
            resp = {}

        return resp

    def thread_heart_report(self):
        # 上报心跳数据
        system_info = {
            "detail": {
                # "disk": json.dumps(self.cur_system_info.get_disk()),
                "memory": json.dumps(self.cur_system_info.get_memory_info()),
                "agentId": self.dt_agent_id,
                "cpu": json.dumps({"rate": self.cur_system_info.get_cpu_rate()}),
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
            logger.info("report heart data success")
        else:
            logger.error("report heart data error")

        # 创建并初始化线程
        t1 = threading.Timer(self.interval, self.thread_heart_report)
        # 启动线程
        t1.start()

    def agent_register(self, data):

        url = "/api/v1/agent/register"

        server_env = dict(os.environ)
        server_env_arr = []
        project_name = self.config_data.get("project", {}).get("name", "Demo Project")
        if isinstance(server_env, dict):
            if server_env.get("projectName", ""):
                project_name = server_env.get("projectName", "")
            elif server_env.get("PROJECTNAME", ""):
                # windows always upper case env key
                project_name = server_env.get("PROJECTNAME", "")

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
            "pid": str(os.getpid())
        }
        resp = self.base_report(url, register_data)
        if resp.get("status", 0) == 201:
            self.dt_agent_id = resp.get("data", {}).get("id", 0)
            if self.dt_agent_id:
                # 创建并初始化线程
                t1 = threading.Timer(self.interval, self.thread_heart_report)
                # 启动线程
                t1.start()

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
