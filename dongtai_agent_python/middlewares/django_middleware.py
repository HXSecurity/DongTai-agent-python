import django
import dongtai_agent_python.global_var as dt_global_var
from django.utils.deprecation import MiddlewareMixin
from dongtai_agent_python.common.content_tracert import set_current, delete_current, dt_tracker_set
from dongtai_agent_python.report.upload_data import AgentUpload
from dongtai_agent_python.assess.patch import enable_patches
from dongtai_agent_python.common.logger import logger_config
logger = logger_config("python_agent")


class FireMiddleware(MiddlewareMixin):
    # '''中间键类'''

    def __init__(self, *args, **kwargs):
        # '''服务器重启之后，接受第一个请求时调用'''
        logger.info("python agent init")
        super().__init__(*args, **kwargs)

        self.agent_upload = AgentUpload()
        # register
        cur_middle = {
            "container_name": "Django",
            "container_version": django.get_version()
        }
        dt_global_var.dt_set_value("dt_open_pool", False)
        register_resp = self.agent_upload.agent_register(cur_middle)
        dt_global_var.dt_set_value("dt_open_pool", False)
        if register_resp.get("status", 0) == 201:
            dt_agent_id = register_resp.get("data", {}).get("id", 0)
            logger.info("python agent register success ")
            # 上报心跳数据
        else:
            dt_agent_id = 0
            logger.error("python agent register error ")

        dt_global_var.dt_set_value("agent_id", dt_agent_id)
        print("------begin hook-----")
        enable_patches("django")
        logger.info("python agent hook open")

    def process_request(self, request):
        # '''产生request对象后，url匹配之前调用'''
        func_id = id(request)
        set_current(func_id)
        reg_agent_id = dt_global_var.dt_get_value("agent_id")
        req_count = dt_global_var.dt_get_value("req_count") + 1
        dt_global_var.dt_set_value("req_count", req_count)
        http_url = request.scheme + "://" + request.META.get("HTTP_HOST", "") + request.META.get("PATH_INFO", "")
        if request.META.get("QUERY_STRING", ""):
            http_url += "?" + request.META.get("QUERY_STRING", "")
        http_req_header = self.agent_upload.agent_json_to_str(dict(request.headers))

        if request.body and isinstance(request.body, str):
            reqeust_body = str(request.body, encoding="utf-8")
        else:
            reqeust_body = ""

        need_to_set = {
            "agent_id": reg_agent_id,
            "http_protocol": request.META.get("SERVER_PROTOCOL", "'HTTP/1.1'"),
            "http_client_ip": request.META.get("REMOTE_ADDR", "127.0.0.1"),
            "context_path": request.META.get("PATH_INFO", "/"),
            "http_query_string": request.META.get("QUERY_STRING", ""),
            "http_uri": request.path,
            "http_url": http_url,
            "http_method": request.META.get("REQUEST_METHOD", "None"),
            "app_name": request.META.get("IDE_PROJECT_ROOTS", ""),
            "http_req_header": http_req_header,
            "http_body": reqeust_body,
            "http_scheme": request.scheme,
            "dt_pool_args": [],
            "dt_data_args": [],
            "upload_pool": True,
        }
        for key in need_to_set.keys():
            dt_tracker_set(key, need_to_set[key])

        dt_global_var.dt_set_value("dt_open_pool", True)
        dt_global_var.dt_set_value("have_hooked", [])
        dt_global_var.dt_set_value("hook_exit", False)
        logger.info("hook request api success")

    def process_response(self, request, response):
        # '''视图函数调用之后，内容返回浏览器之前'''
        dt_global_var.dt_set_value("dt_open_pool", False)
        if response.content and isinstance(response.content, str):
            http_res_body = str(response.content, encoding="utf-8")
        else:
            http_res_body = ""
        dt_tracker_set("http_res_body", http_res_body)
        resp_header = dict(response.headers)
        resp_header['agent_id'] = dt_global_var.dt_get_value("agent_id")
        http_res_header = self.agent_upload.agent_json_to_str(resp_header)
        dt_tracker_set("http_res_header", http_res_header)
        logger.info("hook api response success")

        self.agent_upload.agent_upload_report()
        # 避免循环嵌套
        dt_tracker_set("upload_pool", False)
        delete_current()

        return response