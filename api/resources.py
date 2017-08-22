"""
Created on 10.08.2017
Updated on 10.08.2017
@author: Eemeli Ristimella
@author: Annukka Tormala
@author: Jenni Tormala
@author: Johirul Islam
"""


# imports
import time
from datetime import datetime
import json
from flask import Flask, request, Response, g, _request_ctx_stack, redirect, send_from_directory, render_template, session
from flask.ext.restful import Resource, Api, abort
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import jinja2

from utils import RegexConverter
import engine


# Initialize app
socketio = SocketIO()
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
socketio.init_app(app)
app.debug = True
# Allow cross-origin resources
cors = CORS(app)
#cors = CORS(app, resources={r"/*": {"origins": "http://localhost:port"}})

# Secret Key used for sessions
app.secret_key = '\x00-Gs\xdc\x05EP/\x0e\xc6=\x91\x03<i\x19qL:\\\xa0\xc4\xfb'

# Set the database Engine. In order to modify the database file (e.g. for
# testing) provide the database path   app.config to modify the
#database to be used (for instance for testing)
app.config.update({'Engine': engine.Engine()})
#Start the RESTful API.
api = Api(app)


#Add the Regex Converter so we can use regex expressions when we define the
#routes
#app.url_map.converters["regex"] = RegexConverter


#Constants for hypermedia formats and profiles
MASON = "application/vnd.mason+json"
JSON = "application/json"
CHIRRUP_USER_PROFILE = "/profiles/user-profile/"
CHIRRUP_MESSAGE_PROFILE = "/profiles/message-profile/"
ERROR_PROFILE = "/profiles/error-profile"

ATOM_THREAD_PROFILE = "https://tools.ietf.org/html/rfc4685"

# Fill these in
APIARY_PROFILES_URL = "http://docs.chirrup.apiary.io/#reference/profiles"
APIARY_RELS_URL = "http://docs.chirrup.apiary.io/#reference/link-relations"

USER_SCHEMA_URL = "/chirrup/schema/user/"
LINK_RELATIONS_URL = "/chirrup/link-relations/"


# These two classes below are how we make producing the resource representation
# JSON documents manageable and resilient to errors. As noted, our mediatype is
# Mason. Similar solutions can easily be implemented for other mediatypes.

class MasonObject(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@title": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)        
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs

class ChirrupObject(MasonObject):    
    """
    A convenience subclass of MasonObject that defines a bunch of shorthand 
    methods for inserting application specific objects into the document. This
    class is particularly useful for adding control objects that are largely
    context independent, and defining them in the resource methods would add a 
    lot of noise to our code - not to mention making inconsistencies much more
    likely!

    In the chirrup code this object should always be used for root document as 
    well as any items in a collection type resource. 
    """

    def __init__(self, **kwargs):
        """
        Calls dictionary init method with any received keyword arguments. Adds
        the controls key afterwards because hypermedia without controls is not 
        hypermedia. 
        """

        super(ChirrupObject, self).__init__(**kwargs)
        self["@controls"] = {}

    def add_control_users_all(self):
        """
        This adds the users-all link to an object. Intended for the document object.  
        """

        self["@controls"]["users-all"] = {
            "href": api.url_for(Users),
            "title": "List users"
        }
		
    def add_control_add_user(self):
        """
        This adds the add-user control to an object. Intended for the 
        document object. Instead of adding a schema dictionary we are pointing
        to a schema url instead for two reasons: 1) to demonstrate both options;
        2) the user schema is relatively large.
        """

        self["@controls"]["add-user"] = {
            "href": api.url_for(Users),
            "method": "POST"
        }
		
    def add_control_add_room(self):
        """
        This adds the add-room control to an object. Intended for the 
        document object. Instead of adding a schema dictionary we are pointing
        to a schema url instead for two reasons: 1) to demonstrate both options;
        2) the user schema is relatively large.
        """

        self["@controls"]["add-room"] = {
            "href": api.url_for(Rooms),
            "method": "POST"
        }

#ERROR HANDLERS

def create_error_response(status_code, title, message=None):
    """ 
    Creates a: py: class:`flask.Response` instance when sending back an
    HTTP error response

    : param integer status_code: The HTTP status code of the response
    : param str title: A short description of the problem
    : param message: A long description of the problem
    : rtype:: py: class:`flask.Response`
    """

    resource_url = None
    #We need to access the context in order to access the request.path
    ctx = _request_ctx_stack.top
    if ctx is not None:
        resource_url = request.path
    envelope = MasonObject(resource_url=resource_url)
    envelope.add_error(title, message)

    return Response(json.dumps(envelope), status_code, mimetype=MASON+";"+ERROR_PROFILE)

@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, "Resource not found",
                                 "This resource url does not exit")

@app.errorhandler(400)
def malformed_input_format(error):
    return create_error_response(400, "Malformed input format",
                                 "The format of the input is incorrect")

@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, "Error",
                    "The system has failed. Please, contact the administrator")


@app.before_request
def connect_db():
    '''Creates a database connection before the request is processed.

    The connection is stored in the application context variable flask.g .
    Hence it is accessible from the request object.'''
    print('opening db onnection')
    g.con = app.config['Engine'].connect()


@app.teardown_request
def close_connection(exc):
    ''' Closes the database connection
        Check if the connection is created. It might be exception appear before
        the connection is created.'''

    print('closing db connection')
    if hasattr(g, 'con'):
        g.con.close()
		
class Users(Resource):

    def get(self):
        '''
        Gets a list of all the rooms from the database.
        '''
        #Create the users list
        users_db = g.con.get_users()
        
        #FILTER AND GENERATE THE RESPONSE
        #Create the envelope
        envelope = ChirrupObject()

        envelope.add_control_add_user()                                                            
        envelope.add_control("self", href=api.url_for(Users))

        items = envelope["users-all"] = []

        for user in users_db:
            item = ChirrupObject(
                user_id=user["user_id"],
                username=user["username"],
                email=user["email"],
                status=user["status"],
                created=user["created"],
                updated=user["updated"],
                nickname=user["nickname"],
                image=user["image"]
            )
            item.add_control("self", href=api.url_for(User, userid=user["user_id"]))
            items.append(item)
        
        #RENDER
        return envelope, 200

    def post(self):
        """
        Add a new user in the database.
        """

        if JSON != request.headers.get("Content-Type", ""):
            abort(415)
        create_error_response(415, "Error", "Your content types be fail")
        # PARSE THE REQUEST:
        request_body = request.get_json(force=True)
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         )
        # Get the request body and serialize it to object
        # We should check that the format of the request body is correct. Check
        # That mandatory attributes are there.

        # pick up username so we can check for conflicts		
        try:
            username = request_body["username"]
        except KeyError:
            return create_error_response(400, "Username required!", "Please provide username in the request")

        # Conflict if user already exist
        if g.con.contains_username(username):
            return create_error_response(409, "Username exists!", "Username %s already exists." % username)
		
        # pick up email so we can check for conflicts
        try:
            email = request_body["email"]
        except KeyError:
            return create_error_response(400, "Email required!", "Please provide email in the request")

        # Conflict if user already exist
        if g.con.contains_email(email):
            return create_error_response(409, "Email exists!", "Email %s already exists." % email)

        # pick up nickname so we can check for conflicts
        try:
            nickname = request_body["nickname"]
        except KeyError:
            return create_error_response(400, "Nickname required!", "Please provide nickname in the request")

        # Conflict if user already exist
        if g.con.contains_nickname(nickname):
            return create_error_response(409, "Nickname exists!", "Nickname %s already exists." % nickname)

        # pick up rest of the optional fields
        image = request_body.get("image", None)
		
        user = {"public_profile": {"nickname": nickname,
                                   "image": image},
                "private_profile": {"username": username,
                                       "email": email}
                }

        try:
            user_id = g.con.append_user(user)
        except ValueError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all"
                                         " mandatory properties"
                                         )

        # CREATE RESPONSE AND RENDER
        return Response(status=201, headers={"Location": api.url_for(User, userid=user_id)})
		
class User(Resource):
    """
    User Resource. Public and private profile are separate resources.
    """

    def get(self, userid):
        """
        Get basic information of a user.
        """

        user = g.con.get_user(userid)

        if user is None:
		    # if user not found
            return resource_not_found(404)
		
        envelope = ChirrupObject()

        envelope.add_control("delete", href=api.url_for(User, userid=userid), method='DELETE')
        envelope.add_control("private-data", encoding='json', href=api.url_for(Users), method='GET', title='user\'s private data')

        item = ChirrupObject(
            user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            status=user["status"],
            created=user["created"],
            updated=user["updated"],
            nickname=user["nickname"],
            image=user["image"]
        )
        item.add_control("self", href=api.url_for(User, userid=userid))
        item.add_control("user", href=api.url_for(Users))
        envelope['users-info'] = item

        string_data = json.dumps(envelope)
        return Response(string_data, 200, mimetype=MASON+";"+ERROR_PROFILE)
		
    	
    def put(self, userid):
        """
        Modify an existing user in the database.
        """
        # CHECK THAT USER EXISTS
        if not g.con.contains_user(userid):
            return create_error_response(400, "User does not exist",
                                         "There is no a user with id %s" % userid
                                         )

        user = g.con.get_user(userid)
										 
        if JSON != request.headers.get("Content-Type", ""):
            abort(415)
        create_error_response(415, "Error", "Your content types be fail")
        # PARSE THE REQUEST:
        request_body = request.get_json(force=True)
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         )
        # Get the request body and serialize it to object
        # We should check that the format of the request body is correct. Check
        # That mandatory attributes are there.

        # pick up nickname so we can check for conflicts
        try:
            nickname = request_body["nickname"]
        except KeyError:
            return create_error_response(400, "Nickname required!", "Please provide nickname in the request")

        # Conflict if user already exist
        if g.con.contains_nickname(nickname):
            return create_error_response(409, "Nickname exists!", "Nickname %s already exists." % nickname)

        # pick up rest of the optional fields
        image = request_body.get("image", None)
		
        if image is None:
            if user['image'] is not None:
			    # user[image]='/images/image.jpg'
				# so we need to extract 'image.jpg' from user['image'] 
				# using python substring except '/images/' that is first 7 character
                print user['image']
                print user['image'][8:]
                image = user['image'][8:]
		
        user = {
					"public_profile": 
						{
							"nickname": nickname,
							"image": image
						},
					"private_profile": 
						{
							"username": user['username'],
                            "email": user['email']
						}
                }
        
        try:
            user_id = g.con.modify_user(userid, user)
            envelope = ChirrupObject(message='The user information is modified correctly.')
            envelope.add_control('self', href=api.url_for(User, userid=userid))
            status_code = 204
        except ValueError:
            envelope = ChirrupObject(resource_url=api.url_for(User, userid=userid))
            envelope.add_error(title='User does not exist', messages='User does not exist')
            status_code = 400

        # CREATE RESPONSE AND RENDER
        string_data = json.dumps(envelope)
        #return Response(string_data, status_code, mimetype=MASON+";"+ERROR_PROFILE)
        return Response(string_data, 200, mimetype=MASON+";"+ERROR_PROFILE)
		
    def delete(self, userid):
        """
        Delete a user in the system.

       : param int userid: user id of the required user.

        RESPONSE STATUS CODE:
         * If the user is deleted returns 204.
         * If the nickname does not exist return 404
        """

        if g.con.delete_user(userid):
            #envelope = ChirrupObject(message='The user was successfully deleted.')
            #return envelope, 204
            return "The user was successfully deleted.", 204
        else:
            # Send error message
            return create_error_response(404, "Unknown user", "There is no user with id %s" % userid)

class Rooms(Resource):

    def get(self):
        '''
        Gets a list of all the rooms from the database.
        '''
        #Create the rooms list
        rooms_db = g.con.get_rooms()
        
        #FILTER AND GENERATE THE RESPONSE
        #Create the envelope
        envelope = ChirrupObject()

        envelope.add_control_add_room()                                                            
        envelope.add_control("self", href=api.url_for(Rooms))

        items = envelope["rooms-all"] = []

        for room in rooms_db:
            item = ChirrupObject(
                room_id=room["room_id"],
                name=room["name"],
                admin=room["admin"],
                created=room["created"],
                updated=room["updated"]
            )
            item.add_control("self", href=api.url_for(Room, roomid=room["room_id"]))
            items.append(item)
        
        #RENDER
        return envelope, 200
		
    def post(self):
        """
        Add a new room in the database.
        """

        if JSON != request.headers.get("Content-Type", ""):
            abort(415)
        create_error_response(415, "Error", "Your content types be fail")
        # PARSE THE REQUEST:
        request_body = request.get_json(force=True)
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         )
        # Get the request body and serialize it to object
        # We should check that the format of the request body is correct. Check
        # That mandatory attributes are there.

        # pick up username so we can check for conflicts		
        try:
            name = request_body["name"]
        except KeyError:
            return create_error_response(400, "Room name required!", "Please provide room name in the request")

        # Conflict if user already exist
        if g.con.contains_room_name(name):
            return create_error_response(409, "Room name exists!", "Room name %s already exists." % name)
		
        # pick up admin
        try:
            admin = request_body["admin"]
        except KeyError:
            return create_error_response(400, "Admin id required!", "Please provide admin's in the request")
			
        # check wheather admin exist or not
        if g.con.get_user_nickname(admin) is None:
            return create_error_response(409, "No admin exists!", "No admin found with id %s." % admin)
		
        # pick up type
        try:
            type = request_body["type"]
        except KeyError:
            return create_error_response(400, "Type id required!", "Please provide type in the request")
			
        # check wheather admin exist or not
        if type not in ['PUBLIC', 'PRIVATE']:
            return create_error_response(409, "Invalid room type!", "Room type '%s' is not correct. It should be either 'PUBLIC' of 'PRIVATE'." % type)

        try:
            room_id = g.con.create_room(name, type, admin)
        except ValueError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all"
                                         " mandatory properties"
                                         )

        # CREATE RESPONSE AND RENDER
        return Response(status=201, headers={"Location": api.url_for(Room, roomid=room_id)})

class Room(Resource):
    """
    Room Resource.
    """

    def get(self, roomid):
        """
        Get basic information of a room.
        """

        room = g.con.get_room(roomid)

        if room is None:
		    # if room not found
            return resource_not_found(404)
		
        envelope = ChirrupObject()

        item = ChirrupObject(
            room_id=room["room_id"],
            name=room["name"],
            admin=room["admin"],
            created=room["created"],
            updated=room["updated"]
        )
        item.add_control("self", href=api.url_for(Room, roomid=roomid))
        item.add_control("rooms", href=api.url_for(Rooms))
        envelope['rooms-info'] = item

        string_data = json.dumps(envelope)
        return Response(string_data, 200, mimetype=MASON+";"+ERROR_PROFILE)
		
    def delete(self, roomid):
        """
        Delete a room from the system.

       : param int roomid: room id of the required room to be deleted.

        RESPONSE STATUS CODE:
         * If the room is deleted returns 204.
         * If the room does not exist return 404
        """

        if g.con.delete_room(roomid):
            #envelope = ChirrupObject(message='The user was successfully deleted.')
            #return envelope, 204
            return "The room was successfully deleted.", 204
        else:
            # Send error message
            return create_error_response(404, "Unknown room", "There is no room with id %s" % roomid)

class Messages(Resource):

    def get(self, roomid):
        '''
        Gets a list of all the rooms from the database.
        '''
        #Create the rooms list
        messages_db = g.con.get_messages(roomid)
        
        #FILTER AND GENERATE THE RESPONSE
        #Create the envelope
        envelope = ChirrupObject()                                                       
        envelope.add_control("self", href=api.url_for(Messages, roomid=roomid))

        items = envelope["room-messages"] = []
		
        if messages_db:
            for message in messages_db:
                item = ChirrupObject(
                    content=message["content"],
                    sender=message["user_id"],
                    timestamp=message["created"]
                )
                item.add_control("self", href=api.url_for(Message, messageid=message["message_id"]))
                items.append(item)
        
        #RENDER
        return envelope, 200
		
    def post(self, roomid):
        """
        Add a new message in the database.
        """

        if JSON != request.headers.get("Content-Type", ""):
            abort(415)
        create_error_response(415, "Error", "Your content types be fail")
        # PARSE THE REQUEST:
        request_body = request.get_json(force=True)
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         )
        # Get the request body and serialize it to object
        # We should check that the format of the request body is correct. Check
        # That mandatory attributes are there.
		
        # check wheather roomid exist or not
        if g.con.get_room_name(roomid) is None:
            return create_error_response(409, "No such room exists!", "No such room found with id %s." % roomid)
		
        # pick up sender
        try:
            sender = request_body["sender"]
        except KeyError:
            return create_error_response(400, "Sender id required!", "Please provide sender's in the request")
			
        # check wheather sender exist or not
        if g.con.get_user_nickname(sender) is None:
            return create_error_response(409, "No sender exists!", "No sender found with id %s." % sender)

        # pick up content		
        try:
            content = request_body["content"]
        except KeyError:
            return create_error_response(400, "Content required!", "Please provide content in the request")
		
        timestamp = int(time.mktime(datetime.now().timetuple()))
			
        try:
            message_id = g.con.create_message(roomid, sender, content, timestamp)
        except ValueError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all"
                                         " mandatory properties"
                                         )

        # CREATE RESPONSE AND RENDER
        return Response(status=201, headers={"Location": api.url_for(Message, messageid=message_id)})

class Message(Resource):
    """
    Room Resource.
    """

    def get(self, messageid):
        """
        Get basic information of a room.
        """

        message = g.con.get_message(messageid)

        if message is None:
		    # if message not found
            return resource_not_found(404)
		
        envelope = ChirrupObject()

        item = ChirrupObject(
            message_id=message["message_id"],
            room_id=message["room_id"],
            sender=message["user_id"],
            content=message["content"],
            created=message["created"]
        )
        item.add_control("self", href=api.url_for(Message, messageid=message["message_id"]))
        envelope['messages-info'] = item

        string_data = json.dumps(envelope)
        return Response(string_data, 200, mimetype=MASON+";"+ERROR_PROFILE)
		
    def delete(self, messageid):
        """
        Delete a room from the system.

       : param int roomid: room id of the required room to be deleted.

        RESPONSE STATUS CODE:
         * If the room is deleted returns 204.
         * If the room does not exist return 404
        """

        if g.con.delete_message(messageid):
            #envelope = ChirrupObject(message='The user was successfully deleted.')
            #return envelope, 204
            return "The message was successfully deleted.", 204
        else:
            # Send error message
            return create_error_response(404, "Unknown message", "There is no message with id %s" % messageid)
		
class Members(Resource):

    def get(self, roomid):
        '''
        Gets a list of all the rooms from the database.
        '''
        room = g.con.get_room(roomid)
        if room is None:
            return resource_not_found(404)
			
        #Create the rooms list
        members_db = g.con.get_members(room_id=roomid)
        
        #FILTER AND GENERATE THE RESPONSE
        #Create the envelope
        envelope = ChirrupObject()                                                       
        envelope.add_control("self", href=api.url_for(Members, roomid=roomid))

        items = envelope["room-members"] = []
		
        if members_db:
            for member in members_db:
                item = ChirrupObject(
                    id=member["id"],
                    room_id=member["user_id"],
                    user_id=member["user_id"],
                    joined=member["joined"]
                )
                #item.add_control("self", href=api.url_for(Message, messageid=message["message_id"]))
                items.append(item)
        
        #RENDER
        return envelope, 200

#Define the routes
api.add_resource(Users, '/users/', endpoint='users')
api.add_resource(User, '/users/<int:userid>/', endpoint='user')
api.add_resource(Rooms, '/rooms/', endpoint='rooms')
api.add_resource(Room, '/rooms/<int:roomid>/', endpoint='room')
api.add_resource(Messages, '/rooms/<int:roomid>/messages/', endpoint='messages')
api.add_resource(Message, '/messages/<int:messageid>/', endpoint='message')
api.add_resource(Members, '/rooms/<int:roomid>/members/', endpoint='members')


# Socket IO events, dynamic namespaces not supported, so common namespace '/chat' is used.
# SocketIO rooms separate message broadcasting.
@socketio.on('joined', namespace='/chat')
def joined(event_data):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    # Probably a web token or some other authentication mechanism is also passed to identify users, which is
    # currently not yet implemented.

    room_name = event_data["room_name"]
    nickname = event_data["nickname"]
    print('room_name:', room_name)

    g.con = app.config['Engine'].connect()

    # Check that nickname and room exist
    user_id = g.con.get_user_id(nickname)
    if user_id is None:
        # Send personal error message to user using unique session id
        join_room(request.sid)
        print('User doesn\'t exist')
        emit('status', {'msg': 'Nickname' + nickname + ' doesn\'t exist'}, room=request.sid)
        leave_room(request.sid)
        return

    room_id = g.con.get_room_id(room_name)
    if room_id is None:
        # Send personal error message to user using unique session id
        join_room(request.sid)
        #print('Room with id' + room_id + 'doesn\'t exist')
        emit('status', {'msg': 'Room  ' + room_name + ' doesn\'t exist'}, room=request.sid)
        leave_room(request.sid)
        return

    # Store user_id and nickname to server side session so that we don't need to fetch the id every time
    #print('user_id: ', user_id)
    session['nickname'] = nickname
    session['user_id'] = user_id
    session['room_id'] = room_id

    #print(room_id, '', nickname)

    join_room(room_name)
    emit('status', {'msg': nickname + ' has connected.'}, room=room_name)

    # add user to online list, not implemented


@socketio.on('text', namespace='/chat')
def text(event_data):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room_name = event_data["room_name"]
    nickname = session["nickname"]
    user_id = session["user_id"]
    room_id = session["room_id"]
    #print(room_name, '', nickname)
    message = event_data["msg"]
    emit('message', {'msg': nickname + ':' + message}, room=room_name)
    # write message to db, sql injection?
    g.con = app.config['Engine'].connect()
    g.con.create_message(room_id, user_id, message, int(time.mktime(datetime.now().timetuple())))
    # db connection is closed automatically


@socketio.on('left', namespace='/chat')
def left(event_data):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room_name = event_data["room_name"]
    nickname = session["nickname"]
    #print(room_id, '', nickname)
    leave_room(room_name)
    emit('status', {'msg': nickname + ' has disconnected.'}, room=room_name)
    # remove from online list, not implemented

#Start the application
#DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == '__main__':
    #Debug true activates automatic code reloading and improved error messages
    #app.run(debug=True)
    socketio.run(app)
