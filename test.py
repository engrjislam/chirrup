import api.engine
import sqlite3


engine = api.engine.Engine('db/chirrup.db')
con = engine.connect()
m1 = con.get_message(1)
m2 = con.get_message(2)

con.set_foreign_keys_support()

con.con.row_factory = sqlite3.Row
cur = con.con.cursor()

NEW_USER = {
    'public_profile': {
        'nickname': 'Birdperson',
        'image': 'worms.jpg'},
    'private_profile': {
        'username': 'birdperson1',
        'email': 'birdperson@gmail.com',
        'status': 'ACTIVE',
        'created': '1362017481'
    }
}
NEW_ROOM = {
    'name': 'some_room',
    'type': 'PUBLIC',
    'admin': '7'
}

#user_id = con.append_user(NEW_USER)
#print('user_id: ', user_id)
#user = con.get_user(11)

rooms = con.get_rooms()
print(rooms)

rooms2 = con.get_rooms(before=2147483642, keyword='1')
print(rooms2)

rooms3 = con.get_rooms(after=1, keyword='room', number_of_rooms=3)
print(rooms3)

messages = con.get_messages(room_id=1, before=2147483642, after=1, number_of_messages=4)
print('messages: ', messages)


con.close()
