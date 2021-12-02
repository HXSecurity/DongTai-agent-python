import django

from dongtai_agent_python.middlewares.wsgi_middleware import WSGIMiddleware
from dongtai_agent_python.setting import const


class DjangoWSGIMiddleware(WSGIMiddleware):
    def __init__(self, wsgi_app):
        super(DjangoWSGIMiddleware, self).__init__(wsgi_app, {
            "name": const.CONTAINER_DJANGO,
            "version": django.get_version()
        })
