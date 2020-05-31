from VinsFramework import *

if __name__ == '__main__':
    app = create_app()


    run_app('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)