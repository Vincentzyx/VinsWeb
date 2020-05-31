import os
from typing import Any
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.utils import redirect
from werkzeug.serving import run_simple
from jinja2 import Environment, FileSystemLoader

class VFrame(object):

    def __init__(self, config={}):
        pass

    def dispatch_request(self, request):
        return Response('Hello World!')

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app(with_static=True):
    app = VFrame()
    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static':  os.path.join(os.path.dirname(__file__), 'static')
        })
    return app


def run_app(hostname: Any, port: Any, application: Any, use_reloader: bool = False, use_debugger: bool = False,
            use_evalex: bool = True, extra_files: Any = None, reloader_interval: int = 1, reloader_type: str = "auto",
            threaded: bool = False, processes: int = 1, request_handler: Any = None, static_files: Any = None,
            passthrough_errors: bool = False, ssl_context: Any = None):

    run_simple(hostname, port, application, use_reloader, use_debugger, use_evalex, extra_files, reloader_interval,
               reloader_type, threaded, processes, request_handler, static_files, passthrough_errors, ssl_context)