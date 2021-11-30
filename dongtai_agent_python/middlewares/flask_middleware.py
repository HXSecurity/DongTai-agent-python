import flask
from flask import request

from dongtai_agent_python import CONTEXT_TRACKER
from dongtai_agent_python.common.logger import logger_config
from dongtai_agent_python.context import RequestContext, FlaskRequest
from dongtai_agent_python.middlewares.base_middleware import BaseMiddleware
from dongtai_agent_python.utils import scope
from dongtai_agent_python.setting import const

logger = logger_config("python_agent")


class AgentMiddleware(BaseMiddleware):
    def __init__(self, old_app, app):
        self.old_wsgi_app = old_app

        super(AgentMiddleware, self).__init__({
            "name": const.CONTAINER_FLASK,
            "version": flask.__version__
        })

        @app.before_request
        def process_request_hook(*args, **kwargs):
            # agent paused
            if self.setting.is_agent_paused():
                return

            context = RequestContext(FlaskRequest(request))
            CONTEXT_TRACKER.set_current(context)

        @app.after_request
        def process_response_hook(response):
            if self.setting.is_agent_paused():
                return response

            context = CONTEXT_TRACKER.current()

            process_response_data(context, response)

            context.detail['pool'] = context.pool
            data = {
                'detail': context.detail,
                'type': 36,
            }
            self.openapi.async_report_upload(self.executor, data)

            return response

        @scope.with_scope(scope.SCOPE_AGENT)
        def process_response_data(context, response):
            if not response.is_streamed and response.data and isinstance(response.data, bytes):
                http_res_body = bytes.decode(response.data, "utf-8", errors="ignore")
            else:
                http_res_body = ""

            resp_header = dict(response.headers)
            resp_header['agentId'] = self.setting.agent_id

            context.extract_response(resp_header, response.status_code, http_res_body)

    def __call__(self, *args, **kwargs):
        obj = self.old_wsgi_app(*args, **kwargs)
        CONTEXT_TRACKER.delete_current()
        return obj
