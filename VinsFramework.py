import os
from typing import Any
from functools import wraps
import json
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.utils import redirect
from werkzeug.urls import url_parse
from werkzeug.serving import run_simple
from jinja2 import Environment, FileSystemLoader
import requests


class vException(Exception):
    pass

class VFrame(object):
    url_rule_class = Rule

    def __init__(self, config={}):
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path), autoescape=True)
        self.url_map = Map([])
        self.view_functions = {}

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype='text/html')

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            response = self.view_functions.get(endpoint)(request, **values)
            if isinstance(response, str):
                response = Response(response)
            return response
        except NotFound:
            print("Url ", request, " not found.")
            response = self.render_template("404.html")
            response.status_code = 404
            return response
        except HTTPException as e:
            print("Internal error: ", e)
            response = self.render_template("500.html")
            response.status_code = 500
            return response

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def route(self, rule, **options):
        def decorator(func):
            endpoint = options.pop("endpoint", None)
            self.add_url_rule(rule, endpoint, func, **options)
            return func
        return decorator

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        if endpoint is None:
            endpoint = view_func.__name__
        options['endpoint'] = endpoint
        methods = options.pop('methods', None)
        if methods is None:
            methods = getattr(view_func, 'methods', None) or ('GET',)
        methods = set(item.upper() for item in methods)
        required_methods = set(getattr(view_func, 'required_methods', ()))
        provide_automatic_options = getattr(view_func, 'provide_automatic_options', None)
        if provide_automatic_options is None:
            if 'OPTIONS' not in methods:
                provide_automatic_options = True
                required_methods.add('OPTIONS')
            else:
                provide_automatic_options = False

        methods |= required_methods
        rule = self.url_rule_class(rule, methods=methods, **options)
        rule.provide_automatic_options = provide_automatic_options
        self.url_map.add(rule)

        if view_func is not None:
            old_func = self.view_functions.get(endpoint)
            if old_func is not None and old_func != view_func:
                raise AssertionError('Endpoint already exist:'
                                     ' %s' % endpoint)
            self.view_functions[endpoint] = view_func

    @staticmethod
    def json_response(func):
        @wraps(func)
        def decorated(*args, **kwargs) -> str:
            res = {
                "code": 0,
                "msg": ""
            }
            data = None
            try:
                data = func(*args, **kwargs)
            except vException as e:
                res["code"] = e.args[0]
                res["msg"] = e.args[1]

            if data is not None:
                res.update({
                    "data": data
                })
            return json.dumps(res, default=str, ensure_ascii=False)
        return decorated

    @staticmethod
    def proxy_to(url):
        def decorator(func):
            def decorated(request):
                req = requests.get(url, params=request.args)
                response = Response(req.content.decode(encoding="utf-8"))
                response.content_type = req.headers['Content-Type']
                return response
            return decorated
        return decorator


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