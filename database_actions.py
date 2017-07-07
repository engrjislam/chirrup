Class User:

Class Message:

Class Room:

def create_room(room):
    '''
    Creates a room to the database.

    :param str nickname: nickname of the target user
    :return: a list of users nicknames or None if ``nickname`` is not in the
        database
    '''

def load_room_messages(roomid, id_start, id_end):
    '''
    Returns the amount of messages specified by id_start, and id_end.
    :param roomid:
    :param message_id_start:
    :param message_id_end:
    :return:
    '''


def delete_room(room_id):
    ''' Deletes the room. '''




def change_room_details(room):



def get_room(room_id):
    ''' Constructs a Room object based on id.'''

def getUser(user_id):
    ''' Constructs a Room object based on id.'''


def get_user_rooms(user_id):
    '''
    Returns all the rooms where user is joined.
    '''
