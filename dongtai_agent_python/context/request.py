import json
from io import BytesIO

from dongtai_agent_python.utils import scope


class Request(object):
    def __init__(self, request):
        super(Request, self).__init__()

        self.scheme = request.scheme
        self.headers = dict(request.headers)


class DjangoRequest(Request):
    def __init__(self, request):
        super(DjangoRequest, self).__init__(request)

        self.environ = request.META
        self.url = self.scheme + "://" + self.environ.get("HTTP_HOST", "") + self.environ.get("PATH_INFO", "")
        if self.environ.get("QUERY_STRING", ""):
            self.url += "?" + self.environ.get("QUERY_STRING", "")

        self.body = self.get_request_body(request)

    @scope.with_scope(scope.SCOPE_AGENT)
    def get_request_body(self, request):
        request_body = ""
        if request.POST:
            forms = []
            for key in request.POST:
                forms.append(key + "=" + request.POST[key])
            request_body = "&".join(forms)
        if request_body == "":
            try:
                req_body = request.META['wsgi.input'].read()
                request._stream.stream = BytesIO(req_body)
                if req_body and isinstance(req_body, bytes):
                    request_body = bytes.decode(req_body, "utf-8", errors="ignore")
            except Exception:
                pass

        return request_body


class FlaskRequest(Request):
    def __init__(self, request):
        super(FlaskRequest, self).__init__(request)

        self.environ = request.environ
        self.url = self.scheme + "://" + self.environ.get("HTTP_HOST", "") + self.environ.get("PATH_INFO", "")
        if self.environ.get("QUERY_STRING", ""):
            self.url += "?" + self.environ.get("QUERY_STRING", "")
        self.body = self.get_request_body(request)

    @scope.with_scope(scope.SCOPE_AGENT)
    def get_request_body(self, request):
        request_body = ""
        if request.is_json and request.json:
            request_body = json.dumps(request.json)
        elif request.form:
            forms = []
            for key in request.form:
                forms.append(key + "=" + request.form[key])
            request_body = "&".join(forms)
        elif request.get_data():
            request_body = bytes.decode(request.get_data(), "utf-8", errors="ignore")

        return request_body
