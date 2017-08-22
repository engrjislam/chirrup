from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from api.resources import app as api
from client.client import app as client

application = DispatcherMiddleware(client, {
    '/api': api
})
if __name__ == '__main__':
    run_simple('localhost', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)