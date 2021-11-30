from http.client import responses

from dongtai_agent_python.utils import utils
from dongtai_agent_python.common.logger import logger_config
from dongtai_agent_python.setting import Setting
from dongtai_agent_python.utils import scope

logger = logger_config("request_context")


class RequestContext(object):
    def __init__(self, request):
        self.has_source = False
        self.hook_exit = False
        self.taint_ids = []
        self.pool = []
        self.tags = {}

        self.setting = Setting()
        self.setting.incr_request_seq()
        self.request = request

        self.detail = {
            "language": "PYTHON",
            "replayRequest": False,
            "agentId": self.setting.agent_id,
            "uri": request.environ.get("PATH_INFO", "/"),
            "url": request.url,
            "queryString": request.environ.get("QUERY_STRING", ""),
            "protocol": request.environ.get("SERVER_PROTOCOL", "'HTTP/1.1'"),
            "contextPath": request.environ.get("PATH_INFO", "/"),
            "clientIp": request.environ.get("REMOTE_ADDR", "127.0.0.1"),
            "method": request.environ.get("REQUEST_METHOD", "None"),
            "reqHeader": utils.json_to_base64(request.headers),
            "reqBody": request.body,
            "scheme": request.scheme,
        }

        logger.info("hook request success")

    @scope.with_scope(scope.SCOPE_AGENT)
    def extract_response(self, header, status_code, body):
        protocol = self.request.environ.get("SERVER_PROTOCOL", "'HTTP/1.1'")
        status_line = protocol + " " + str(status_code) + " " + responses[status_code]
        header['agentId'] = self.setting.agent_id

        res_header = utils.normalize_response_header(status_line, header)
        self.detail['resHeader'] = res_header
        self.detail['resBody'] = body

        logger.info("hook response success")
