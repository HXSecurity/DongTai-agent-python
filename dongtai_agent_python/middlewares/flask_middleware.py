from flask import request, jsonify
import dongtai_agent_python.global_var as dt_global_var
from dongtai_agent_python.common.content_tracert import current_thread_id, dt_tracker, set_current, delete_current, \
    dt_tracker_set
from dongtai_agent_python.report.upload_data import AgentUpload
from dongtai_agent_python.assess.patch import enable_patches
from dongtai_agent_python.common.logger import logger_config
from concurrent.futures import ThreadPoolExecutor
import json,flask
logger = logger_config("python_agent")


class AgentTest(object):
    def __init__(self, old_app):
        print("__init__ old content txt")
        self.old_content = old_app

    def __call__(self, *args, **kwargs):

        obj = self.old_content(*args,**kwargs)
        return obj


class AgentMiddleware(object):
    def __init__(self, old_app,app):
        print("__init__ app")
        self.old_wsgi_app = old_app

        logger.info("python agent init")
        self.executor = ThreadPoolExecutor()
        self.agent_upload = AgentUpload()
        # register
        cur_middle = {
            "container_name": "flask",
            "container_version": flask.__version__
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
        print("------begin hook-----")
        enable_patches("flask")
        logger.info("python agent hook open")

        @app.before_request
        def process_request_hook(*args, **kwargs):

            request_body = {}
            if request.is_json and request.json:
                request_body = request.json
            elif request.form:
                for item in request.form:
                    request_body[item] = request.form[item]

            func_id = id(request)
            set_current(func_id)
            reg_agent_id = dt_global_var.dt_get_value("agentId")
            req_count = dt_global_var.dt_get_value("req_count") + 1
            dt_global_var.dt_set_value("req_count", req_count)

            request_header = dict(request.headers)
            http_req_header = self.agent_upload.agent_json_to_str(request_header)
            request_body = self.agent_upload.agent_json_to_str(request_body)

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

            dt_global_var.dt_set_value("dt_open_pool", True)
            dt_global_var.dt_set_value("have_hooked", [])
            dt_global_var.dt_set_value("hook_exit", False)
            logger.info("hook request api success")

        @app.after_request
        def process_response_hook(response):

            dt_global_var.dt_set_value("dt_open_pool", False)
            if response.data and isinstance(response.data, str):
                http_res_body = str(response.data, encoding="utf-8")
            else:
                http_res_body = ""
            dt_tracker_set("resBody", http_res_body)
            resp_header = dict(response.headers)
            resp_header['agentId'] = dt_global_var.dt_get_value("agentId")
            http_res_header = self.agent_upload.agent_json_to_str(resp_header)
            dt_tracker_set("resHeader", http_res_header)
            logger.info("hook api response success")

            upload_report = dt_tracker[current_thread_id()]
            self.executor.submit(self.agent_upload.agent_upload_report, upload_report)
            # 避免循环嵌套
            dt_tracker_set("upload_pool", False)
            delete_current()

            return response

        @app.before_first_request
        def first():
            print("before_first_request.....")
            print("before_first_request.....")
            pass

    def __call__(self, *args, **kwargs):

        obj = self.old_wsgi_app(*args,**kwargs)
        return obj



