from http.client import responses
from io import BytesIO

import django

import dongtai_agent_python.global_var as dt_global_var
from dongtai_agent_python.common import origin, utils
from dongtai_agent_python.common.content_tracert import current_thread_id, delete_current, dt_tracker, dt_tracker_set, \
    set_current
from dongtai_agent_python.common.logger import logger_config
from dongtai_agent_python.middlewares.base_middleware import BaseMiddleware

logger = logger_config("python_agent")


class FireMiddleware(BaseMiddleware):
    # '''中间键类'''

    def __init__(self, get_response=None):
        self.get_response = get_response

        super(FireMiddleware, self).__init__({
            "module_name": "django",
            "container_name": "Django",
            "container_version": django.get_version()
        })

    def __call__(self, request):
        dt_global_var.dt_set_value("dt_open_pool", False)
        # agent paused
        if dt_global_var.is_pause():
            dt_global_var.dt_set_value("dt_open_pool", True)
            return self.get_response(request)

        # '''产生request对象后，url匹配之前调用'''
        request_id = id(request)
        set_current(request_id)
        reg_agent_id = dt_global_var.dt_get_value("agentId")
        req_count = dt_global_var.dt_get_value("req_count") + 1
        dt_global_var.dt_set_value("req_count", req_count)
        http_url = request.scheme + "://" + request.META.get("HTTP_HOST", "") + request.META.get("PATH_INFO", "")
        if request.META.get("QUERY_STRING", ""):
            http_url += "?" + request.META.get("QUERY_STRING", "")
        http_req_header = utils.json_to_base64(dict(request.headers))

        request_body = ""
        if request.POST:
            forms = []
            for key in request.POST:
                origin.list_append(forms, key + "=" + request.POST[key])
            request_body = origin.str_join("&", forms)
        if request_body == "":
            try:
                req_body = request.META['wsgi.input'].read()
                request._stream.stream = BytesIO(req_body)
                if req_body and isinstance(req_body, bytes):
                    request_body = req_body.decode("utf-8", errors="ignore")
            except Exception as e:
                pass
        dt_tracker_set("reqBody", request_body)

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
            "scheme": request.scheme,
            "dt_pool_args": [],
            "dt_data_args": [],
            "upload_pool": True,
        }
        for key in need_to_set.keys():
            dt_tracker_set(key, need_to_set[key])

        dt_global_var.dt_set_value("have_hooked", [])
        dt_global_var.dt_set_value("hook_exit", False)
        logger.info("hook request api success")

        dt_global_var.dt_set_value("dt_open_pool", True)
        return self.process_response(request)

    def process_response(self, request):
        # '''视图函数调用之后，内容返回浏览器之前'''
        dt_global_var.dt_set_value("dt_open_pool", True)
        response = self.get_response(request)
        dt_global_var.dt_set_value("dt_open_pool", False)

        if not response.streaming and response.content and isinstance(response.content, bytes):
            http_res_body = response.content.decode("utf-8", errors="ignore")
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

        dt_global_var.dt_set_value("dt_open_pool", True)
        return response
