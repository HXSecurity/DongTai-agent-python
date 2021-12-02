import flask

from dongtai_agent_python.middlewares.wsgi_middleware import WSGIMiddleware
from dongtai_agent_python.setting import const


class FlaskWSGIMiddleware(WSGIMiddleware):
    def __init__(self, app):
        super(FlaskWSGIMiddleware, self).__init__(app.wsgi_app, {
            "name": const.CONTAINER_FLASK,
            "version": flask.__version__
        })
