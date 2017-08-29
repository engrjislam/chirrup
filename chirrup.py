from flask import Flask, render_template
from client.client import app as client

@client.route('/user/<int:userid>')
def user_page(userid):
    return render_template('profile_page.html', userid=userid);

@client.route('/room/<int:roomid>')
def room_page(roomid):
    return render_template('index.html', roomid=roomid);

@client.route('/rooms')
def rooms_page():
    return render_template('rooms_list.html');

@client.route('/add_user')
def add_user():
    return render_template('add_user.html');

@client.route('/add_room')
def add_room():
    return render_template('create_room.html');

if __name__ == '__main__':
    client.run(debug=True, port=5001)