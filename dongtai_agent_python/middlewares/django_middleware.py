import django

from dongtai_agent_python import CONTEXT_TRACKER
from dongtai_agent_python.common.logger import logger_config
from dongtai_agent_python.context import RequestContext, DjangoRequest
from dongtai_agent_python.middlewares.base_middleware import BaseMiddleware
from dongtai_agent_python.utils import scope
from dongtai_agent_python.setting import const

logger = logger_config("python_agent")


class FireMiddleware(BaseMiddleware):
    def __init__(self, get_response=None):
        self.get_response = get_response

        super(FireMiddleware, self).__init__({
            "name": const.CONTAINER_DJANGO,
            "version": django.get_version()
        })

    def __call__(self, request):
        # agent paused
        if self.setting.is_agent_paused():
            return self.get_response(request)

        context = RequestContext(DjangoRequest(request))
        with CONTEXT_TRACKER.lifespan(context):
            return self.process_response(context, request)

    def process_response(self, context, request):
        response = self.get_response(request)

        self.process_response_data(context, response)

        context = CONTEXT_TRACKER.current()
        context.detail['pool'] = context.pool
        data = {
            'detail': context.detail,
            'type': 36,
        }
        self.openapi.async_report_upload(self.executor, data)

        return response

    @scope.with_scope(scope.SCOPE_AGENT)
    def process_response_data(self, context, response):
        if not response.streaming and response.content and isinstance(response.content, bytes):
            http_res_body = bytes.decode(response.content, "utf-8", errors="ignore")
        else:
            http_res_body = ""

        if hasattr(response, 'headers'):
            # django >= 3.2
            # https://docs.djangoproject.com/en/3.2/releases/3.2/#requests-and -responses
            resp_header = dict(response.headers)
        else:
            # django < 3.2
            resp_header = dict(response._headers)

        context.extract_response(resp_header, response.status_code, http_res_body)
