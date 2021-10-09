import requests, gzip, json, os, socket, base64, uuid, time, threading
import dongtai_agent_python.global_var as dt_global_var
from dongtai_agent_python.common.content_tracert import dt_tracker, current_thread_id
from dongtai_agent_python.common.logger import logger_config
logger = logger_config("upload_data")


def PrintNetIfAddr():
    try:
        import psutil
        dic = psutil.net_if_addrs()
        network_arr = []
        for adapter in dic:
            snicList = dic[adapter]
            mac = '无 mac 地址'
            ipv4 = '无 ipv4 地址'
            ipv6 = '无 ipv6 地址'
            for snic in snicList:
                if snic.family.name in {'AF_LINK', 'AF_PACKET'}:
                    mac = snic.address
                elif snic.family.name == 'AF_INET':
                    ipv4 = snic.address
                elif snic.family.name == 'AF_INET6':
                    ipv6 = snic.address
            network_arr.append('%s, %s, %s, %s' % (adapter, mac, ipv4, ipv6))
        logger.info("get network success")
        return ";".join(network_arr)
    except Exception as e:
        logger.error("get network fail" + str(e))
        return ""


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
    def PrintNetIfAddr(self):
        if self.psutil is not None:
            try:
                dic = self.psutil.net_if_addrs()
                network_arr = []
                for adapter in dic:
                    snicList = dic[adapter]
                    mac = '无 mac 地址'
                    ipv4 = '无 ipv4 地址'
                    ipv6 = '无 ipv6 地址'
                    for snic in snicList:
                        if snic.family.name in {'AF_LINK', 'AF_PACKET'}:
                            mac = snic.address
                        elif snic.family.name == 'AF_INET':
                            ipv4 = snic.address
                        elif snic.family.name == 'AF_INET6':
                            ipv6 = snic.address
                    network_arr.append('%s, %s, %s, %s' % (adapter, mac, ipv4, ipv6))
                logger.info("get network success")
                return ";".join(network_arr)
            except Exception as e:
                logger.error("get network" + str(e))
                return ""
        else:
            return ""

    # 获取cpu信息
    def getCpuRate(self):
        if self.psutil is not None:
            # print(self.psutil.cpu_percent())
            percent = self.psutil.cpu_percent()
            return percent
        else:
            return 0

    # 获取系统内存使用情况
    def getMemoryInfo(self):
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
    def getDisk(self):
        disk = {"info": []}
        if self.psutil is not None:
            devs = self.psutil.disk_partitions()
            if devs:
                for dev in devs:
                    diskinfo = self.psutil.disk_usage(dev.mountpoint)
                    # 将字节转换成G
                    disk['info'].append({
                        "name": dev.device,
                        "total": str(round(diskinfo.total/self.unit,2))+"G",
                        "used": str(round(diskinfo.used/self.unit,2))+"G",
                        "free": str(round(diskinfo.free/self.unit,2))+"G",
                        "rate": str(diskinfo.percent)+"%",
                        "fstype": dev.fstype
                    })
        return disk


class AgentUpload(object):

    def __init__(self):
        self.config_data = dt_global_var.dt_get_value("config_data")
        self.dt_agent_id = 0
        self.interval = self.config_data.get("iast", {}).get("service", {}).get("report", {}).get("interval",30)
        self.cur_system_info = {}
        self.headers = {
            "Authorization": "Token " + self.config_data.get("iast", {}).get("server", {}).get("token", ""),
            "user-agent": "DongTaiIAST-Agent",
            'content-encoding': 'gzip',
            'content-type': "application/json"
        }

    def agent_json_to_str(self,json_data):
        if json_data:
            new_list = []
            for item in json_data.keys():
                new_list.append(str(item)+"="+str(json_data[item]))
            json_data = "\n".join(new_list)
            json_data = base64.b64encode(json_data.encode('utf-8'))
            json_data = json_data.decode('utf-8')
        return json_data

    # 获取接口信息
    def base_api_get(self, url):
        url = self.config_data.get("iast", {}).get("server", {}).get("url", "") + url
        try:
            res = requests.get(url, timeout=20, headers=self.headers)
            Resp = res.content.decode("utf-8")
            Resp = json.loads(Resp)

            # logger.info("report base data")
        except Exception as e:
            logger.error("report data error" + str(e))
            Resp = {}

        return Resp

    def base_report(self, url, body):
        url = self.config_data.get("iast", {}).get("server", {}).get("url", "") + url
        print(body)
        stream_data = json.dumps(body)

        body_data = gzip.compress(stream_data.encode('utf-8'))
        try:
            res = requests.post(url, data=body_data, timeout=20, headers=self.headers)
            print(res.content)
            Resp = res.content.decode("utf-8")
            Resp = json.loads(Resp)

            # logger.info("report base data")
        except Exception as e:
            logger.error("report data error" + str(e))
            Resp = {}

        return Resp

    def thread_heart_report(self):

        # 上报心跳数据
        system_info = {
            "detail": {
                "cpu": json.dumps({"rate": self.cur_system_info.getCpuRate()}),
                "disk": json.dumps(self.cur_system_info.getDisk()),
                "memory": json.dumps(self.cur_system_info.getMemoryInfo()),
                "agent_id": self.dt_agent_id,
                "req_count": dt_global_var.dt_get_value("req_count"),
                "report_queue": 0,
                "method_queue": 0,
                "replay_queue": 0
            },
            "type": 1
        }
        url = "/api/v1/report/upload"
        heartResp = self.base_report(url, system_info)
        if heartResp.get("status", 0) == 201:
            logger.info("report heart data success")
        else:
            logger.error("report heart data error")

        # 创建并初始化线程
        t1 = threading.Timer(self.interval, self.thread_heart_report)
        # 启动线程
        t1.start()

    def agent_register(self, data):

        url = "/api/v1/agent/register"

        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        mac_id = ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
        # print(mac_id)
        server_env = dict(os.environ)
        agent_name = ""
        server_env_arr = []
        project_name = "Demo Project"
        if isinstance(server_env,dict):
            if server_env.get("projectName", ""):
                project_name = server_env.get("projectName", "")
            else:
                project_name = self.config_data.get("project", {}).get("name", "Demo Project")
            agent_name = server_env.get("PATH", "/").split("/")[-1] + "-" + server_env.get("USER", "")

            for key in server_env.keys():

                server_env_arr.append(key+"="+str(server_env[key]) )

        env_str = ",".join(server_env_arr)

        server_env_str = base64.b64encode(env_str.encode('utf-8'))
        self.cur_system_info = SystemInfo()
        network_info = self.cur_system_info.PrintNetIfAddr()
        version = self.config_data.get("engine", {}).get("version", "v1.0.0")
        register_data = {
            "name": agent_name + "-"+version+"-" + str(mac_id)+"-"+str(id(time.time())),
            "project_name": project_name,
            "version": version,
            "language": "PYTHON",
            "hostname": socket.gethostname(),
            "network": network_info,
            "container_name": data.get("container_name", ""),
            "container_version": data.get("container_version", ""),
            "web_server_addr": "",
            "web_server_port": "",
            "web_server_path": "",
            "server_env": server_env_str.decode('utf-8'),
            "pid": str(os.getpid())
        }
        Resp = self.base_report(url, register_data)
        if Resp.get("status", 0) == 201:
            self.dt_agent_id = Resp.get("data", {}).get("id", 0)
            if self.dt_agent_id:
                # 创建并初始化线程
                t1 = threading.Timer(self.interval, self.thread_heart_report)
                # 启动线程
                t1.start()

        return Resp

    def agent_upload_report(self):

        url = "/api/v1/report/upload"
        upload_report = dt_tracker[current_thread_id()]
        Resp = self.base_report(url, upload_report)

        return Resp

    def get_policy_config(self):

        url = "/api/v1/profiles?language_id=2"
        Resp = self.base_api_get(url)

        return Resp