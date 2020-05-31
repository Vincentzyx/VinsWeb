from VinsFramework import *

app = create_app()

# Use jinja2 to render template
@app.route("/")
def index(request):
    return app.render_template("index.html", msg="球球了 让我过吧，后面考核我一定重视/(ㄒoㄒ)/~~")

# Easy access to Json API
@app.route("/api")
@app.json_response
def api_1(request):
    return "This msg will be convert to json automatically"

@app.route("/api2")
@app.json_response
def api_2(request):
    raise vException(-1, "This error will be gracefully packed into json, with code and msg.")

# Reverse Proxy without configuring nginx
@app.route("/baidu")
@app.proxy_to("https://www.baidu.com")
def baidu(request):
    pass

if __name__ == '__main__':
    run_app('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
