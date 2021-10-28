import time
from concurrent.futures import ThreadPoolExecutor
from http.client import responses

import django

import dongtai_agent_python.global_var as dt_global_var
from dongtai_agent_python.assess.patch import enable_patches
from dongtai_agent_python.common import utils
from dongtai_agent_python.common.content_tracert import current_thread_id, delete_current, dt_tracker, dt_tracker_set, \
    set_current
from dongtai_agent_python.common.logger import logger_config
from dongtai_agent_python.report.upload_data import AgentUpload

logger = logger_config("python_agent")


class FireMiddleware(object):
    # '''中间键类'''

    def __init__(self, get_response=None):
        # '''服务器重启之后，接受第一个请求时调用'''
        start_time = time.time_ns()

        logger.info("python agent init")
        self.get_response = get_response

        self.executor = ThreadPoolExecutor()
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

        dt_global_var.dt_set_value("agentId", dt_agent_id)
        logger.debug("------begin hook-----")
        enable_patches("django")

        self.agent_upload.report_startup_time((time.time_ns() - start_time) / 1000000)
        logger.info("python agent hook open")

    def __call__(self, request):
        # agent paused
        if dt_global_var.is_pause():
            return self.get_response(request)

        # '''产生request对象后，url匹配之前调用'''
        func_id = id(request)
        set_current(func_id)
        reg_agent_id = dt_global_var.dt_get_value("agentId")
        req_count = dt_global_var.dt_get_value("req_count") + 1
        dt_global_var.dt_set_value("req_count", req_count)
        http_url = request.scheme + "://" + request.META.get("HTTP_HOST", "") + request.META.get("PATH_INFO", "")
        if request.META.get("QUERY_STRING", ""):
            http_url += "?" + request.META.get("QUERY_STRING", "")
        http_req_header = utils.json_to_base64(dict(request.headers))

        if request.body and isinstance(request.body, bytes):
            request_body = utils.bytes_to_base64(request.body)
        else:
            request_body = ""

        need_to_set = {
            "agentId": reg_agent_id,
            "uri": request.path,
            "url": http_url,
            "queryString": request.META.get("QUERY_STRING", ""),
            "protocol": request.META.get("SERVER_PROTOCOL", "'HTTP/1.1'"),
            "contextPath": request.META.get("PATH_INFO", "/"),
            "clientIp": request.META.get("REMOTE_ADDR", "127.0.0.1"),
            "method": request.META.get("REQUEST_METHOD", "None"),
            "reqHeader": http_req_header,
            "reqBody": request_body,
            "scheme": request.scheme,
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

        return self.process_response(request)

    def process_response(self, request):
        # '''视图函数调用之后，内容返回浏览器之前'''
        response = self.get_response(request)

        dt_global_var.dt_set_value("dt_open_pool", False)
        if not response.streaming and response.content and isinstance(response.content, bytes):
            http_res_body = utils.bytes_to_base64(response.content)
        else:
            http_res_body = ""
        dt_tracker_set("resBody", http_res_body)

        if hasattr(response, 'headers'):
            # django >= 3.2
            # https://docs.djangoproject.com/en/3.2/releases/3.2/#requests-and -responses
            resp_header = dict(response.headers)
        else:
            # django < 3.2
            resp_header = dict(response._headers)

        protocol = request.META.get("SERVER_PROTOCOL", "'HTTP/1.1'")
        status_line = protocol + " " + str(response.status_code) + " " + responses[response.status_code]
        resp_header['agentId'] = dt_global_var.dt_get_value("agentId")
        http_res_header = utils.normalize_response_header(status_line, resp_header)
        dt_tracker_set("resHeader", http_res_header)
        logger.info("hook api response success")

        upload_report = dt_tracker[current_thread_id()]
        self.agent_upload.async_agent_upload_report(self.executor, upload_report)
        # 避免循环嵌套
        dt_tracker_set("upload_pool", False)
        delete_current()

        return response
