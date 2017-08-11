"""
Created on 10.08.2017
Updated on 10.08.2017
@author: Eemeli Ristimella
@author: Annukka Tormala
@author: Jenni Tormala
@author: Johirul Islam
"""

# import necessary libraries and utilies
import time
from flask import Flask, request, Response, g
from flask.ext.restful import Resource, Api, abort
from werkzeug.exceptions import NotFound,  UnsupportedMediaType

from utils import RegexConverter
import connections, engine
app = Flask(__name__)
app.debug = True
# Set the database Engine. In order to modify the database file (e.g. for
# testing) provide the database path   app.config to modify the
#database to be used (for instance for testing)
app.config.update({'Engine': engine.Engine()})
#Start the RESTful API.
api = Api(app)


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
        users = []
        for user_db in users_db:
            users.append(user_db)

        #Create the envelope
        envelope = {}
        
        envelope['users-all'] = users
        #RENDER
        return envelope

#Define the routes
api.add_resource(Users, '/users/', endpoint='users')

#Start the application
#DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == '__main__':
    #Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
