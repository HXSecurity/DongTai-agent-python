from http.client import responses

import webob

from dongtai_agent_python import CONTEXT_TRACKER
from dongtai_agent_python.common.logger import logger_config
from dongtai_agent_python.middlewares import BaseMiddleware
from dongtai_agent_python.setting import Setting
from dongtai_agent_python.utils import scope, utils

logger = logger_config("wsgi_middleware")


class WSGIRequest(webob.BaseRequest):
    def __init__(self, environ):
        """
        Django is not fully wsgi-compliant, so we need its request body to be passed in
        explicitly.
        """
        super(WSGIRequest, self).__init__(environ)


class WSGIRequestContext(object):
    def __init__(self, environ):
        scope.enter_scope(scope.SCOPE_AGENT)

        self.environ = environ
        self.request = WSGIRequest(environ)

        self.has_source = False
        self.taint_ids = []
        self.pool = []
        self.tags = {}

        self.setting = Setting()
        self.setting.incr_request_seq()

        req_header = {}
        for header_key, header_value in self.request.headers.items():
            req_header[header_key] = header_value

        self.detail = {
            "language": "PYTHON",
            "replayRequest": False,
            "agentId": self.setting.agent_id,
            "uri": environ.get("PATH_INFO", "/"),
            "url": self.request.url,
            "queryString": environ.get("QUERY_STRING", ""),
            "protocol": environ.get("SERVER_PROTOCOL", "'HTTP/1.1'"),
            "contextPath": environ.get("PATH_INFO", "/"),
            "clientIp": environ.get("REMOTE_ADDR", "127.0.0.1"),
            "method": environ.get("REQUEST_METHOD", "None"),
            "reqHeader": utils.json_to_base64(req_header),
            "reqBody": self.request.body.decode('utf-8', errors='ignore'),
            "scheme": self.request.scheme,
        }

        logger.info("hook request success")
        scope.exit_scope()

    @scope.with_scope(scope.SCOPE_AGENT)
    def extract_response(self, response):
        protocol = self.environ.get("SERVER_PROTOCOL", "'HTTP/1.1'")
        status_line = protocol + " " + str(response.status_code) + " " + responses[response.status_code]

        res_header = {}
        for header_key, header_value in response.headers.items():
            res_header[header_key] = header_value
        res_header['agentId'] = self.setting.agent_id

        self.detail['resHeader'] = utils.normalize_response_header(status_line, res_header)

        body = response.body
        res_body = ''
        if isinstance(body, bytes):
            res_body = body.decode('utf-8', errors='ignore')
        if isinstance(body, str):
            res_body = body
        self.detail['resBody'] = res_body

        logger.info("hook response success")


class WSGIMiddleware(BaseMiddleware):
    def __init__(self, wsgi_app, container):
        self.wsgi_app = wsgi_app

        super(WSGIMiddleware, self).__init__(container)

    def __call__(self, environ, start_response):
        context = WSGIRequestContext(environ)
        with CONTEXT_TRACKER.lifespan(context):
            return self.process_response(context, environ, start_response)

    def process_response(self, context, environ, start_response):
        try:
            response = WSGIRequest(environ).get_response(self.wsgi_app)
            context.extract_response(response)

            return response(environ, start_response)
        finally:
            context.detail['pool'] = context.pool
            data = {
                'detail': context.detail,
                'type': 36,
            }
            self.openapi.async_report_upload(self.executor, data)
