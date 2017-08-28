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
from flask import Flask, request, Response, g, _request_ctx_stack, redirect, send_from_directory
from flask.ext.restful import Resource, Api, abort

import engine


app = Flask(__name__)
app.debug = True
# Set the database Engine. In order to modify the database file (e.g. for
# testing) provide the database path   app.config to modify the
#database to be used (for instance for testing)
app.config.update({'Engine': engine.Engine()})
#Start the RESTful API.
api = Api(app)


#Constants for hypermedia formats and profiles
MASON = "application/vnd.mason+json"
JSON = "application/json"
CHIRRUP_USER_PROFILE = "/profiles/user-profile/"
CHIRRUP_MESSAGE_PROFILE = "/profiles/message-profile/"
CHIRRUP_ROOM_PROFILE = "/profiles/room-profile/"
ERROR_PROFILE = "/profiles/error-profile"

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
            "encoding": "json",
            "method": "POST",
            "schema": self._user_schema(edit=False)
        }
		
    def add_control_edit_user(self, userid):
        """
        This adds the add-user control to an object. Intended for the 
        document object. Instead of adding a schema dictionary we are pointing
        to a schema url instead for two reasons: 1) to demonstrate both options;
        2) the user schema is relatively large.
        """

        self["@controls"]["edit"] = {
            "href": api.url_for(User, userid=userid),
            "method": "DELETE",
            "schema": self._user_schema(edit=True)
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
		
    def add_control_add_room_for_user(self):
        """
        This adds the add-room control to an object. Intended for the 
        document object. Instead of adding a schema dictionary we are pointing
        to a schema url instead for two reasons: 1) to demonstrate both options;
        2) the user schema is relatively large.
        """

        self["@controls"]["add-room"] = {
            "href": api.url_for(Rooms),
            "method": "POST",
			"encoding": "json",
			"schema": self._room_schema()
        }
		
    def add_control_join_or_leave_room(self, roomid, join = True):
        """
        This adds the join-room or leave-room control to an object. Intended for the 
        document object. Instead of adding a schema dictionary we are pointing
        to a schema url instead for two reasons: 1) to demonstrate both options;
        2) the join-room/leave-room schema is relatively large.
        """

        if join:
            join_or_leave_url = api.url_for(JoinRoom, roomid=roomid)
            join_or_leave = "join"
        else:
            join_or_leave_url = api.url_for(LeaveRoom, roomid=roomid)
            join_or_leave = "leave"

        self["@controls"][join_or_leave] = {
            "href": join_or_leave_url,
            "encoding": "json",
            "method": "POST",
            "schema": self._join_or_leave_room_schema()
        }
		
    def _user_schema(self, edit=False):
        """
        Creates a schema dictionary for users. 
		
        This schema can also be accessed from the urls /chirrup/schema/add-user/.

        : param: None
        : rtype:: dict
        """

        if not edit: 
            required = ["username", "email", "nickname"]
        else: 
            required = ["nickname"]
		
        schema = {
            "type": "object",
            "properties": {},
            "required": required
        }

        props = schema["properties"]
        
        if not edit:
            props["username"] = {
                "title": "Username for login",
                "type": "string"
            }
            props["email"] = {
                "title": "Email address",
                "type": "string"
            }
			
        props["nickname"] = {
            "title": "Nickname in chat",
            "type": "string"
        }
        props["image"] = {
            "title": "Path to profile picture",
            "type": "string"
        }
        '''
        props[user_field] = {
            "title": user_field.capitalize(),
            "description": "Nickname of the message {}".format(user_field),
            "type": "string"
        }
        '''
        return schema
		
    def _join_or_leave_room_schema(self):
        """
        Creates a schema dictionary for rooms. 
		
        This schema can also be accessed from the urls 
        /chirrup/schema/join-room/ and /chirrup/schema/join-room/.

        : param: None
        : rtype:: dict
        """

        required = ["user_id"]
		
        schema = {
            "type": "object",
            "properties": {},
            "required": required
        }

        props = schema["properties"]
			
        props["user_id"] = {
            "title": "Unique user identificate",
            "type": "integer"
        }
		
        return schema
		
    def _room_schema(self):
        """
        Creates a schema dictionary for rooms. 
		
        This schema can also be accessed from the urls 
        /chirrup/schema/join-room/ and /chirrup/schema/join-room/.

        : param: None
        : rtype:: dict
        """

        required = ["name", "admin"]
		
        schema = {
            "type": "object",
            "properties": {},
            "required": required
        }

        props = schema["properties"]
			
        props["name"] = {
            "title": "Name of the room",
            "type": "string"
        }
			
        props["admin"] = {
            "title": "Admin user_id",
            "type": "integer"
        }
		
        return schema
	
    	
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
    '''Creates a database connection before the request is proccessed.

    The connection is stored in the application context variable flask.g .
    Hence it is accessible from the request object.'''

    g.con = app.config['Engine'].connect()

@app.teardown_request
def close_connection(exc):
    ''' Closes the database connection
        Check if the connection is created. It migth be exception appear before
        the connection is created.'''
    if hasattr(g, 'con'):
        g.con.close()
		
class Users(Resource):
    """
    Resource Users implementation
    """

    def get(self):
        '''
        Gets a list of all the users in the database.

        It returns always status code 200.

        RESPONSE ENTITY BODY:

         OUTPUT:
            * Media type: application/vnd.mason+json
                https://github.com/JornWildt/Mason
            * Profile: CHIRRUP_USER_PROFILE
                /profiles/user-profile
        
        Semantic descriptions used in items: user_id, username, email, status, created, updated, nickname, image
        
        NOTE:
         * The attribute nickname and image is obtained from the column 
              users_profile.nickname and users_profile.image
         * The rest of attributes match one-to-one with column names in the user.
        '''
        #Create the users list
        users_db = g.con.get_users()
        
        #FILTER AND GENERATE THE RESPONSE
        #Create the envelope
        envelope = ChirrupObject()
        envelope.add_namespace("chirrup", LINK_RELATIONS_URL)

        envelope.add_control_add_user()                                                            
        envelope.add_control("self", href=api.url_for(Users))

        items = envelope["users-all"] = []

        for user in users_db:
            userid = g.con.get_user_id(user["public_profile"]["nickname"])
            item = ChirrupObject(
                user_id=userid,
                username=user["private_profile"]["username"],
                email=user["private_profile"]["email"],
                status=user["private_profile"]["status"],
                created=user["private_profile"]["created"],
                updated=user["private_profile"]["updated"],
                nickname=user["public_profile"]["nickname"],
                image=user["public_profile"]["image"]
            )
            item.add_control("self", href=api.url_for(User, userid=g.con.get_user_id(user["public_profile"]["nickname"])))
            item.add_control("profile", href=CHIRRUP_USER_PROFILE)
            item.add_control("delete", href=api.url_for(User, userid=userid), method="DELETE")
            items.append(item)
        
        #RENDER
        #return envelope, 200
        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+CHIRRUP_USER_PROFILE)

    def post(self):
        """
        Add a new user in the database.

        REQUEST ENTITY BODY:
         * Media type: JSON
         * Profile: CHIRRUP_USER_PROFILE
           /profiles/user-profile

        Semantic descriptors used in template: username(mandatory),
        email(mandatory), nickname(mandatory), image(optional).

        RESPONSE STATUS CODE:
         * Returns 201 + the url of the new resource in the Location header
         * Return 409 Conflict if there is another user with the same nickname
         * Return 400 if the body is not well formed
         * Return 415 if it receives a media type != application/json

        NOTE:
         * The attribute nickname and image is obtained from the column 
               users_profile.nickname and users_profile.image
         * The rest of attributes match one-to-one with column names in the user.

        NOTE:
        The: py: method:`Connection.append_user()` receives as a parameter a
        dictionary with the following format.
		
        {
            "public_profile":
                {
                    "nickname":"",
                    "image":""
                },
            "private_profile":
                {
                    "username":"",
                    "email":""
                }
        }
			
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
        return Response(status=201, headers={"Location": api.url_for(User, userid=user_id)}, mimetype=MASON+";"+CHIRRUP_USER_PROFILE)
		
class User(Resource):
    """
    User Resource. Public and private profile are separate resources.
    """

    def get(self, userid):
        """
        Get basic information of a user.

        INPUT PARAMETER:
        : param str userid: user id of the required user.

        OUTPUT:
         * Return 200 if the userid exists.
         * Return 404 if the userid is not stored in the system.

        RESPONSE ENTITY BODY:

        * Media type recommended: application/vnd.mason+json
        * Profile recommended: CHIRRUP_USER_PROFILE
                /profiles/user-profile

        Link relations used: self, collection, users-rooms.

        Semantic descriptors used: user_id, username, email, status, created,
        updated, nickname, and image.

        NOTE:
        The: py: method:`Connection.get_user()` returns a dictionary with the
        the following format.

        {
		    "user_id": "1234",
		    "username": "ChatterMaster",
		    "email": "chatterboy@gmail.com",
		    "status": "ACTIVE",
		    "created": "1500906228",
		    "updated": "NULL",
		    "nickname": "Gunnar",
		    "image": "/images/image.png",
        }
        """

        user = g.con.get_user(userid)

        if user is None:
		    # not stored in the system
            return resource_not_found(404)

        item = ChirrupObject(
            user_id=userid,
            username=user["private_profile"]["username"],
            email=user["private_profile"]["email"],
            status=user["private_profile"]["status"],
            created=user["private_profile"]["created"],
            updated=user["private_profile"]["updated"],
            nickname=user["public_profile"]["nickname"],
            image=user["public_profile"]["image"]
        )
        envelope = item
        
        envelope.add_namespace("chirrup", LINK_RELATIONS_URL)
		
        item.add_control("self", href=api.url_for(User, userid=userid))
        item.add_control("profile", href=CHIRRUP_USER_PROFILE)
        envelope.add_control("users", href=api.url_for(Users))
        envelope.add_control("user-rooms", href=api.url_for(UserRooms, userid=userid))
        envelope.add_control_edit_user(userid)
		
        item.add_control("user", href=api.url_for(Users))
        

        string_data = json.dumps(envelope)
        return Response(string_data, 200, mimetype=MASON+";"+CHIRRUP_USER_PROFILE)
		   	
    def put(self, userid):
        """
        Modifies the nickname, image properties of this user.

        INPUT PARAMETERS:
       : param int userid: The id of the user to be edited

        REQUEST ENTITY BODY:
        * Media type: JSON
        * Profile: CHIRRUP_USER_PROFILE
          /profiles/user-profile

        The body should be a JSON document that matches the schema for editing users
        If image is not there consider it remains as before.

        OUTPUT:
         * Returns 204 if the user is modified correctly
         * Returns 400 if the body of the request is not well formed or it is
           empty.
         * Returns 404 if there is no user with userid
         * Returns 415 if the input is not JSON.
         * Returns 500 if the database cannot be modified

        NOTE:
         * The attribute nickname is obtained from the column user_profile.nickname
         * The attribute image is obtained from the column user_profile.image

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
            if user["public_profile"]['image'] is not None:
			    # user[image]='/images/image.jpg'
				# so we need to extract 'image.jpg' from user['image'] 
				# using python substring except '/images/' that is first 7 character
                image = user["public_profile"]['image'][8:]
		
        user = {
					"public_profile": 
						{
							"nickname": nickname,
							"image": image
						},
					"private_profile": 
						{
							"username": user["private_profile"]['username'],
                            "email": user["private_profile"]['email']
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
        return Response(string_data, status_code, mimetype=MASON+";"+CHIRRUP_USER_PROFILE)
        #return Response(string_data, 200, mimetype=MASON+";"+ERROR_PROFILE)
		
    def delete(self, userid):
        """
        Delete a user in the system.

       : param int userid: user id of the required user.

        RESPONSE STATUS CODE:
         * If the user is deleted returns 204.
         * If the nickname does not exist return 404
        """

        if g.con.delete_user(userid):
            envelope = ChirrupObject(message='The user was successfully deleted.')
            #return envelope, 204
            #return "The user was successfully deleted.", 204
            string_data = json.dumps(envelope)
            return Response(string_data, 204, mimetype=MASON+";"+CHIRRUP_USER_PROFILE)
        else:
            # Send error message
            return create_error_response(404, "Unknown user", "There is no user with id %s" % userid)

class Rooms(Resource):
    """
    Resource Rooms implementation
    """

    def get(self):
        '''
        Gets a list of all the rooms from the database.

        It returns always status code 200.

        RESPONSE ENTITY BODY:

         OUTPUT:
            * Media type: application/vnd.mason+json
                https://github.com/JornWildt/Mason
            * Profile: CHIRRUP_ROOM_PROFILE
                /profiles/room-profile
        
        Semantic descriptions used in items: room_id, name, admin, created, updated
        
        NOTE:
         * All the attributes match one-to-one with column names in the room.
        '''
        #Create the rooms list
        rooms_db = g.con.get_rooms()
        
        #FILTER AND GENERATE THE RESPONSE
        #Create the envelope
        envelope = ChirrupObject()
        envelope.add_namespace("chirrup", LINK_RELATIONS_URL)

        envelope.add_control_add_room_for_user()                                                            
        envelope.add_control("self", href=api.url_for(Rooms))

        items = envelope["rooms-all"] = []

        for room in rooms_db:
            roomid = g.con.get_room_id(room["name"])
            item = ChirrupObject(
                room_id=roomid,
                name=room["name"],
                admin=room["admin"],
                created=room["created"],
                updated=room["updated"]
            )
            item.add_control("self", href=api.url_for(Room, roomid=roomid))
            item.add_control("profile", href=CHIRRUP_ROOM_PROFILE)
            item.add_control("messages", href=api.url_for(Messages, roomid=roomid))
            item.add_control("members", href=api.url_for(Members, roomid=roomid))
            items.append(item)
        
        #RENDER
        #return envelope, 200
        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+CHIRRUP_ROOM_PROFILE)
		
    def post(self):
        """
        Add a new room in the database.

        REQUEST ENTITY BODY:
         * Media type: JSON
         * Profile: CHIRRUP_ROOM_PROFILE
           /profiles/room-profile

        Semantic descriptors used in template: name(mandatory),
        admin(mandatory), type(mandatory). status is ACTIVE by default.

        RESPONSE STATUS CODE:
         * Returns 201 + the url of the new resource in the Location header
         * Return 409 Conflict if there is another room with the same name
         * Return 400 if the name, admin, type is not well formed
         * Return 415 if it receives a media type != application/json

        NOTE:
         * All the attributes match one-to-one with column names in the room.

        NOTE:
        The: py: method:`Connection.create_room()` receives name, admin, type.
			
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
			
        # check type
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
        return Response(status=201, headers={"Location": api.url_for(Room, roomid=room_id)}, mimetype=MASON+";"+CHIRRUP_ROOM_PROFILE)

class Room(Resource):
    """
    Room Resource.
    """

    def get(self, roomid):
        """
        Get basic information of a room.
        
        INPUT PARAMETER:
        : param int roomid: room id of the required room.

        OUTPUT:
         * Return 200 if the roomid exists.
         * Return 404 if the roomid is not stored in the system.

        RESPONSE ENTITY BODY:

        * Media type recommended: application/vnd.mason+json
        * Profile recommended: CHIRRUP_ROOM_PROFILE
                /profiles/room-profile

        Link relations used: self, collection.

        Semantic descriptors used: nickname and registrationdate

        NOTE:
        The: py: method:`Connection.get_room()` returns a dictionary with the
        the following format.

        {
		    "room_id": "23471"
            "name": "RandomTalk", 
            "admin": "12543",
            "created": "1500908289",
            "updated": "NULL",
        }
        """

        room = g.con.get_room(roomid)

        if room is None:
		    # if room not found
            return resource_not_found(404)

        envelope = ChirrupObject(
            room_id=roomid,
            name=room["name"],
            admin=room["admin"],
            created=room["created"],
            updated=room["updated"]
        )
        
        envelope.add_namespace("chirrup", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(Room, roomid=roomid))
        envelope.add_control("profile", href=CHIRRUP_ROOM_PROFILE)
        envelope.add_control("messages", href=api.url_for(Messages, roomid=roomid))
        envelope.add_control("members", href=api.url_for(Members, roomid=roomid))
        envelope.add_control("delete", href=api.url_for(Room, roomid=roomid), method="DELETE")
        envelope.add_control_join_or_leave_room(roomid, join = True)
        envelope.add_control_join_or_leave_room(roomid, join = False)

        string_data = json.dumps(envelope)
        return Response(string_data, 200, mimetype=MASON+";"+CHIRRUP_ROOM_PROFILE)
		
    def delete(self, roomid):
        """
        Delete a room from the system.

       : param int roomid: room id of the required room to be deleted.

        RESPONSE STATUS CODE:
         * If the room is deleted returns 204.
         * If the room does not exist return 404
        """

        if g.con.delete_room(roomid):
            envelope = ChirrupObject(message='The user was successfully deleted.')
            #return envelope, 204
            #return "The room was successfully deleted.", 204
            string_data = json.dumps(envelope)
            return Response(string_data, 204, mimetype=MASON+";"+CHIRRUP_ROOM_PROFILE)
        else:
            # Send error message
            return create_error_response(404, "Unknown room", "There is no room with id %s" % roomid)
			
class UserRooms(Resource):
    """
    Resource UserRooms implementation
    """

    def get(self, userid):
        '''
        Gets a list of all the members from the database.

        It returns always status code 200.

        RESPONSE ENTITY BODY:

         OUTPUT:
            * Media type: application/vnd.mason+json
                https://github.com/JornWildt/Mason
        
        Semantic descriptions used in items: user_id, username, email, status, created, updated, nickname, image
        
        NOTE:
         * The attribute nickname and image is obtained from the column 
              users_profile.nickname and users_profile.image
         * The rest of attributes match one-to-one with column names in the user.
        '''
        user = g.con.get_user(userid)
        if user is None:
            return resource_not_found(404)
			
        #Create the rooms list
        user_rooms = g.con.get_user_rooms(userid)
        
        #FILTER AND GENERATE THE RESPONSE
        #Create the envelope
        envelope = ChirrupObject()
        envelope.add_namespace("chirrup", LINK_RELATIONS_URL)                                                       
        envelope.add_control_add_room_for_user()                                                       
        envelope.add_control("self", href=api.url_for(UserRooms, userid=userid))

        items = envelope["items"] = []
		
        if user_rooms:
            for user_room in user_rooms:
                room_id=g.con.get_room_id(user_room["room"]["name"])
                item = ChirrupObject(
                    room_id=room_id,
                    name=user_room["room"]["name"],
                    admin=user_room["room"]["admin"],
                    status=user_room["room"]["status"],
                    created=user_room["room"]["created"],
                    updated=user_room["room"]["updated"],
                    joined=user_room["joined"]
                )
                item.add_control("self", href=api.url_for(Room, roomid=room_id))
                item.add_control("profile", href=CHIRRUP_MESSAGE_PROFILE)
                item.add_control("messages", href=api.url_for(Messages, roomid=room_id))
                item.add_control("members", href=api.url_for(Members, roomid=room_id))
                items.append(item)
        
        #RENDER
        #return envelope, 200
        string_data = json.dumps(envelope)
        return Response(string_data, 200, mimetype=MASON+";"+CHIRRUP_ROOM_PROFILE)
			
class JoinRoom(Resource):
    """
    Resource JoinRoom implementation
    """

    def post(self, roomid):
        '''
        Add an existing user to an exisring room in the database.

        REQUEST ENTITY BODY:
         * Media type: JSON
         * Profile: CHIRRUP_ROOM_PROFILE
           /profiles/room-profile

        Semantic descriptors used in template: user_id(mandatory).

        RESPONSE STATUS CODE:
         * Returns 201 + the url of the new resource in the Location header
         * Return 409 Conflict if there is another room with the same name
         * Return 400 if the user_id is not well formed
         * Return 415 if it receives a media type != application/json

        NOTE:
         * All the attributes match one-to-one with column names in the room_users.

        NOTE:
        The: py: method:`Connection.add_room_member()` receives roomid and userid.
        '''
		
		# check room exists or not
        room = g.con.get_room(roomid)

        if room is None:
		    # if room not found
            return create_error_response(404, "Room not found!", "Room not exists with id %s" % roomid)
		
        if JSON != request.headers.get("Content-Type", ""):
            abort(415)
        create_error_response(415, "Error", "Your content types be fail")
        # PARSE THE REQUEST:
        request_body = request.get_json(force=True)
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         )
		
        # pick up username so we can check for conflicts		
        try:
            userid = request_body["user_id"]
        except KeyError:
            return create_error_response(400, "User id required!", "Please provide user id in the request")
			
		# check user exists or not
        user = g.con.get_user(userid)

        if user is None:
		    # not stored in the system
            return create_error_response(404, "User not found!", "User not exists with id %s" % userid)
			
        try:
            joined = g.con.add_room_member(roomid, userid)
            if joined is False:
                return create_error_response(409, "Unable to join to the room", "User maybe already joined in the room or facing some other problem")
        except ValueError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all"
                                         " mandatory properties"
                                         )
										 
        return Response(status=201, headers={"Location": api.url_for(Room, roomid=roomid)}, mimetype=MASON+";"+CHIRRUP_ROOM_PROFILE)
			
class LeaveRoom(Resource):
    """
    Resource LeaveRoom implementation
    """

    def post(self, roomid):
        '''
        Remove an existing user from an exisring room in the database.

        REQUEST ENTITY BODY:
         * Media type: JSON
         * Profile: CHIRRUP_ROOM_PROFILE
           /profiles/room-profile

        Semantic descriptors used in template: user_id(mandatory).

        RESPONSE STATUS CODE:
         * Returns 204 i the user was removed from the room
         * Return 409 Conflict if there is another room with the same name
         * Return 400 if the user_id is not well formed
         * Return 415 if it receives a media type != application/json

        NOTE:
         * All the attributes match one-to-one with column names in the room_users.

        NOTE:
        The: py: method:`Connection.add_room_member()` receives roomid and userid.
        '''
		
		# check room exists or not
        room = g.con.get_room(roomid)

        if room is None:
		    # if room not found
            return create_error_response(404, "Room not found!", "Room not exists with id %s" % roomid)
		
        if JSON != request.headers.get("Content-Type", ""):
            abort(415)
        create_error_response(415, "Error", "Your content types be fail")
        # PARSE THE REQUEST:
        request_body = request.get_json(force=True)
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         )
		
        # pick up username so we can check for conflicts		
        try:
            userid = request_body["user_id"]
        except KeyError:
            return create_error_response(400, "User id required!", "Please provide user id in the request")
			
		# check user exists or not
        user = g.con.get_user(userid)

        if user is None:
		    # not stored in the system
            return create_error_response(404, "User not found!", "User not exists with id %s" % userid)
			
        try:
            removed = g.con.remove_room_member(roomid, userid)
            if removed:
                envelope = ChirrupObject(message='The user was removed successfully from the room.')
                string_data = json.dumps(envelope)
                return Response(string_data, 204, mimetype=MASON+";"+CHIRRUP_ROOM_PROFILE)
            else:
                return create_error_response(409, "Unable to remove user from the room", "User may not member of the room or facing some other problem")
        except ValueError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all"
                                         " mandatory properties"
                                         )
										 
        #return Response(status=201, headers={"Location": api.url_for(Room, roomid=roomid)}, mimetype=MASON+";"+CHIRRUP_ROOM_PROFILE)
			
class Messages(Resource):
    """
    Resource Messages implementation
    """

    def get(self, roomid):
        '''
        Gets a list of all the rooms from the database.

        It returns always status code 200.

        RESPONSE ENTITY BODY:

         OUTPUT:
            * Media type: application/vnd.mason+json
                https://github.com/JornWildt/Mason
            * Profile: CHIRRUP_MESSAGE_PROFILE
                /profiles/messasge-profile
        
        Semantic descriptions used in items: content, user_id, created
        
        NOTE:
         * All the attributes match one-to-one with column names in the room.
        '''
        #Create the rooms list
        messages_db = g.con.get_messages(roomid)
        
        #FILTER AND GENERATE THE RESPONSE
        #Create the envelope
        envelope = ChirrupObject()
        envelope.add_namespace("chirrup", LINK_RELATIONS_URL)                                                       
        envelope.add_control("self", href=api.url_for(Messages, roomid=roomid))
        envelope.add_control("room-info", href=api.url_for(Room, roomid=roomid))

        items = envelope["messages-all"] = []
		
        if messages_db:
            for message in messages_db:
                item = ChirrupObject(
                    content=message["content"],
                    sender=message["user_id"],
                    timestamp=message["created"]
                )
                item.add_control("self", href=api.url_for(Message, messageid=message["message_id"]))
                item.add_control("profile", href=CHIRRUP_MESSAGE_PROFILE)
                item.add_control("delete", href=api.url_for(Message, messageid=message["message_id"]), method="DELETE")
                items.append(item)
        
        #RENDER
        #return envelope, 200
        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+CHIRRUP_MESSAGE_PROFILE)
		
    def post(self, roomid):
        """
        Add a new message in the database.

        REQUEST ENTITY BODY:
         * Media type: JSON
         * Profile: CHIRRUP_MESSAGE_PROFILE
           /profiles/message-profile

        Semantic descriptors used in template: sender(mandatory), content(mandatory).

        RESPONSE STATUS CODE:
         * Returns 201 + the url of the new resource in the Location header
         * Return 409 Conflict if there is another room with the same name
         * Return 400 if the name, admin, type is not well formed
         * Return 415 if it receives a media type != application/json

        NOTE:
         * All the attributes match one-to-one with column names in the message.

        NOTE:
        The: py: method:`Connection.create_message()` receives sender, content.
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
        return Response(status=201, headers={"Location": api.url_for(Message, messageid=message_id)}, mimetype=MASON+";"+CHIRRUP_MESSAGE_PROFILE)

class Message(Resource):
    """
    Message Resource.
    """

    def get(self, messageid):
        """
        Get basic information of a meesage.

        INPUT PARAMETER:
        : param str userid: user id of the required user.

        OUTPUT:
         * Return 200 if the userid exists.
         * Return 404 if the userid is not stored in the system.

        RESPONSE ENTITY BODY:

        * Media type recommended: application/vnd.mason+json
        * Profile recommended: CHIRRUP_USER_PROFILE
                /profiles/user-profile

        Link relations used: self, collection, users-rooms.

        Semantic descriptors used: message_id, room_id, sender, content, created.

        NOTE:
        :param int messageid: The id of the message.
        The: py: method:`Connection.get_message()` returns a dictionary with the
        the following format.
        :rtype dict like

        {
		    "message_id": 1,
		    "room_id": 1,
		    "sender": 1,
		    "content": "content of the message",
		    "created": "1500906228"
        }
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
        return Response(string_data, 200, mimetype=MASON+";"+CHIRRUP_MESSAGE_PROFILE)
		
    def delete(self, messageid):
        """
        Delete a message from the system.

       : param int messageid: message id of the required meesage to be deleted.

        RESPONSE STATUS CODE:
         * If the room is deleted returns 204.
         * If the room does not exist return 404
        """

        if g.con.delete_message(messageid):
            envelope = ChirrupObject(message='The user was successfully deleted.')
            string_data = json.dumps(envelope)
            #return envelope, 204
            #return "The message was successfully deleted.", 204
            return Response(string_data, 204, mimetype=MASON+";"+CHIRRUP_MESSAGE_PROFILE)
        else:
            # Send error message
            #return create_error_response(404, "Unknown message", "There is no message with id %s" % messageid)
            envelope = ChirrupObject(message="There is no message with id %s" % messageid)	
            string_data = json.dumps(envelope)
            return Response(string_data, 404, mimetype=MASON+";"+ERROR_PROFILE)
		
class Members(Resource):
    """
    Resource Members implementation
    """

    def get(self, roomid):
        '''
        Gets a list of all the members from the database.

        It returns always status code 200.

        RESPONSE ENTITY BODY:

         OUTPUT:
            * Media type: application/vnd.mason+json
                https://github.com/JornWildt/Mason
        
        Semantic descriptions used in items: id, room_id, user_id, joined.
        
        NOTE:
         * The rest of attributes match one-to-one with column names in the user.
        '''
        room = g.con.get_room(roomid)
        if room is None:
            return create_error_response(404, "Room not found!", "Room not exists with id %s" % roomid)
			
        #Create the rooms list
        members_db = g.con.get_members(room_id=roomid)
        
        #FILTER AND GENERATE THE RESPONSE
        #Create the envelope
        envelope = ChirrupObject()
        envelope.add_namespace("chirrup", LINK_RELATIONS_URL)                                              
        envelope.add_control("self", href=api.url_for(Members, roomid=roomid))

        items = envelope["members-all"] = []
		
        if members_db:
            for member in members_db:
                user = g.con.get_user(member["user_id"])
                userid=g.con.get_user_id(user["public_profile"]["nickname"])
                item = ChirrupObject(
                    user_id=userid,
                    username=user["private_profile"]["username"],
                    email=user["private_profile"]["email"],
                    status=user["private_profile"]["status"],
                    created=user["private_profile"]["created"],
                    updated=user["private_profile"]["updated"],
                    nickname=user["public_profile"]["nickname"],
                    image=user["public_profile"]["image"]
                )
                item.add_control("self", href=api.url_for(User, userid=userid))
                item.add_control("profile", href=CHIRRUP_USER_PROFILE)
                items.append(item)
        
        #RENDER
        #return envelope, 200
        string_data = json.dumps(envelope)
        return Response(string_data, 200, mimetype=MASON+";"+CHIRRUP_USER_PROFILE)
		
#Define the routes
api.add_resource(Users, '/users', endpoint='users')
api.add_resource(User, '/users/<int:userid>', endpoint='user')
api.add_resource(Rooms, '/rooms', endpoint='rooms')
api.add_resource(Room, '/rooms/<int:roomid>', endpoint='room')
api.add_resource(UserRooms, '/users/<int:userid>/rooms', endpoint='user-rooms')
api.add_resource(JoinRoom, '/rooms/<int:roomid>/join', endpoint='join-room')
api.add_resource(LeaveRoom, '/rooms/<int:roomid>/leave', endpoint='leave-room')
api.add_resource(Messages, '/rooms/<int:roomid>/messages', endpoint='messages')
api.add_resource(Message, '/messages/<int:messageid>', endpoint='message')
api.add_resource(Members, '/rooms/<int:roomid>/members', endpoint='members')

#Start the application
#DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == '__main__':
    #Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
