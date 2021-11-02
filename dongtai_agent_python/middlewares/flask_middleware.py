from http.client import responses

import flask
from flask import request

import dongtai_agent_python.global_var as dt_global_var
from dongtai_agent_python.common import utils
from dongtai_agent_python.common.content_tracert import current_thread_id, delete_current, dt_tracker, dt_tracker_set, \
    set_current
from dongtai_agent_python.common.logger import logger_config
from dongtai_agent_python.middlewares.base_middleware import BaseMiddleware

logger = logger_config("python_agent")


class AgentMiddleware(BaseMiddleware):
    def __init__(self, old_app, app):
        self.old_wsgi_app = old_app

        super(AgentMiddleware, self).__init__({
            "module_name": "flask",
            "container_name": "Flask",
            "container_version": flask.__version__
        })

        @app.before_request
        def process_request_hook(*args, **kwargs):
            dt_global_var.dt_set_value("dt_open_pool", False)
            # agent paused
            if dt_global_var.is_pause():
                dt_global_var.dt_set_value("dt_open_pool", True)
                return

            request_body = {}
            if request.is_json and request.json:
                request_body = request.json
            elif request.form:
                for item in request.form:
                    request_body[item] = request.form[item]

            request_id = id(request)
            set_current(request_id)
            reg_agent_id = dt_global_var.dt_get_value("agentId")
            req_count = dt_global_var.dt_get_value("req_count") + 1
            dt_global_var.dt_set_value("req_count", req_count)

            request_header = dict(request.headers)
            http_req_header = utils.json_to_base64(request_header)
            request_body = utils.json_to_base64(request_body)

            need_to_set = {
                "agentId": reg_agent_id,
                "uri": request.environ['REQUEST_URI'],
                "url": request.url,
                "queryString": str(request.query_string, encoding="utf-8"),
                "protocol": request.environ['SERVER_PROTOCOL'],
                "contextPath": request.path,
                "clientIp": request.remote_addr,
                "method": request.method,
                "reqHeader": http_req_header,
                "reqBody": request_body,
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

        @app.after_request
        def process_response_hook(response):
            dt_global_var.dt_set_value("dt_open_pool", False)
            # agent paused
            if dt_global_var.is_pause():
                dt_global_var.dt_set_value("dt_open_pool", True)
                return response

            if not response.is_streamed and response.data and isinstance(response.data, bytes):
                http_res_body = utils.bytes_to_base64(response.data)
            else:
                http_res_body = ""
            dt_tracker_set("resBody", http_res_body)
            resp_header = dict(response.headers)

            protocol = request.environ.get("SERVER_PROTOCOL", "'HTTP/1.1'")
            status_line = protocol + " " + str(response.status_code) + " " + responses[response.status_code]
            resp_header['agentId'] = dt_global_var.dt_get_value("agentId")
            http_res_header = utils.normalize_response_header(status_line, resp_header)
            dt_tracker_set("resHeader", http_res_header)
            logger.info("hook api response success")

            upload_report = dt_tracker[current_thread_id()]
            self.agent_upload.async_agent_upload_report(self.executor, upload_report)
            # 避免循环嵌套
            dt_tracker_set("upload_pool", False)

            dt_global_var.dt_set_value("dt_open_pool", True)
            return response

        @app.before_first_request
        def first():
            logger.info("before_first_request.....")
            pass

    def __call__(self, *args, **kwargs):

        obj = self.old_wsgi_app(*args, **kwargs)
        delete_current()
        return obj
