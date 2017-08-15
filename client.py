from flask import Flask, render_template, request, redirect
app = Flask(__name__)

@app.route('/room/')
def index(name=None):
    return render_template('index.html', name=name)

@app.route('/login/')
def login(name=None):
    return render_template('login_page.html', name=name)

@app.route('/add-room/')
def add_room(name=None):
    return render_template('create_room.html', name=name)

@app.route('/rooms/')
def rooms(name=None):
    return render_template('rooms_list.html', name=name)

@app.route('/edit-info/')
def profile(name=None):
    return render_template('profile_page.html', name=name)

@app.route('/logged-out/')
def logout(name=None):
    return render_template('logged_out.html', name=name)    

