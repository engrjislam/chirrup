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
import json
from flask import Flask, request, Response, g, _request_ctx_stack, redirect, send_from_directory
from flask.ext.restful import Resource, Api, abort

from utils import RegexConverter
import engine


app = Flask(__name__)
app.debug = True
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
        This adds the add-user control to an object. Intended ffor the 
        document object. Instead of adding a schema dictionary we are pointing
        to a schema url instead for two reasons: 1) to demonstrate both options;
        2) the user schema is relatively large.
        """

        self["@controls"]["add-user"] = {
            "href": api.url_for(Users),
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

    def get(self):
        '''
        Gets a list of all the users in the database.
        '''
        #Create the messages list
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
        Adds a new user in the database.
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
		
#Define the routes
api.add_resource(Users, '/users/', endpoint='users')
api.add_resource(User, '/users/<int:userid>/', endpoint='user')

#Start the application
#DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == '__main__':
    #Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
