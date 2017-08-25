from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from flask import Flask, render_template
from api.resources import app as api
from client.client import app as client


application = DispatcherMiddleware(api, {
    '/chirrup': client
})


@client.route('/test')
def hello_world():
    return render_template('index.html');

@client.route('/user/<int:userid>')
def user_page(userid):
    return render_template('profile_page.html', userid=userid);

@client.route('/room/<int:roomid>')
def room_page(roomid):
    return render_template('index.html', roomid=roomid);

if __name__ == '__main__':
    run_simple('localhost', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)