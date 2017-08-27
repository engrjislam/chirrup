"""
Created on 21.08.2017
Modified on 21.088.2017
@author: Eemeli Ristimella
@author: Annukka Tormala
@author: Jenni Tormala
@author: Johirul Islam
"""
import unittest, copy
import json

import flask

import api.resources as resources
import api.engine as database
import re

DB_PATH = "db/forum_test.db"
ENGINE = database.Engine(DB_PATH)

MASONJSON = "application/vnd.mason+json"
JSON = "application/json"
CHIRRUP_USER_PROFILE ="/profiles/user-profile/"
CHIRRUP_MESSAGE_PROFILE = "/profiles/message-profile/"
CHIRRUP_ROOM_PROFILE = "/profiles/message-profile/"
CHIRRUP_MESSAGE_PROFILE = "/profiles/message-profile/"

#Tell Flask that I am running it in testing mode.
resources.app.config["TESTING"] = True

#Necessary for correct translation in url_for
resources.app.config["SERVER_NAME"] = "localhost:5000"

#Database Engine utilized in our testing
resources.app.config.update({"Engine": ENGINE})

#Other database parameters.
#initial_messages = 2
#initial_users = 5


class ResourcesAPITestCase(unittest.TestCase):
    #INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        """ Creates the database structure. Removes first any preexisting
            database file
        """
        print "Testing ", cls.__name__
        ENGINE.remove_database()
        ENGINE.create_tables()

    @classmethod
    def tearDownClass(cls):
        """Remove the testing database"""
        print "Testing ENDED for ", cls.__name__
        ENGINE.remove_database()

    def setUp(self):
        """
        Populates the database
        """
        #This method load the initial values from forum_data_dump.sql
        ENGINE.populate_tables()
        #Activate app_context for using url_for
        self.app_context = resources.app.app_context()
        self.app_context.push()
        #Create a test client
        self.client = resources.app.test_client()

    def tearDown(self):
        """
        Remove all records from database
        """
        ENGINE.clear()
        self.app_context.pop()

class UsersTestCase (ResourcesAPITestCase):

    user_1_request = {
	    "username": "testuser1",
        "email": "testuser1@gmail.com",
        "nickname": "testuser1",
        "image": "image1.jpg"
    }

    user_2_request = {
	    "username": "testuser2",
        "email": "testuser2@gmail.com",
        "nickname": "testuser2"
    }
	
	#Existing username
    user_existing_username = {
	    "username": "testuser1",
        "email": "email@gmail.com",
        "nickname": "nickname1"
    }
	
	#Existing nickname
    user_existing_nickname = {
	    "username": "username1",
        "email": "email@gmail.com",
        "nickname": "testuser1"
    }
	
	#Existing email
    user_existing_email = {
	    "username": "username1",
        "email": "testuser1@gmail.com",
        "nickname": "nickname1"
    }

    #Missing username
    user_missing_username = {
        "email": "email@gmail.com",
        "nickname": "nickname1"
    }

    #Missing nickname
    user_missing_nickname = {
        "username": "username1",
        "email": "testuser1@gmail.com"
    }

    #Missing email
    user_missing_email = {
        "username": "username1",
        "nickname": "nickname1"
    }

    def setUp(self):
        super(UsersTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Users,
                                         _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        #NOTE: self.shortDescription() shuould work.
        _url = "/users/"
        print "("+self.test_url.__name__+")", self.test_url.__doc__,
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Users)
			
    def test_get_users(self):
        """
        Checks that GET users return correct status code and data format
        """
        print "("+self.test_get_users.__name__+")", self.test_get_users.__doc__
        #Check that I receive status code 200
        resp = self.client.get(flask.url_for("users"))
        self.assertEquals(resp.status_code, 200)

        # Check that I receive a collection and adequate href
        data = json.loads(resp.data)

        controls = data["@controls"]
        self.assertIn("self", controls)
        self.assertIn("add-user", controls)
        
        self.assertIn("href", controls["self"])
        self.assertEquals(controls["self"]["href"], self.url)
        
        add_ctrl = controls["add-user"]
        self.assertIn("href", add_ctrl)
        self.assertEquals(add_ctrl["href"], "/users/")
        self.assertIn("method", add_ctrl)
        self.assertEquals(add_ctrl["method"], "POST")

        items = data["users-all"]
        #self.assertEquals(len(items), initial_users)
        for item in items:
            self.assertIn("user_id", item)
            self.assertIn("username", item)
            self.assertIn("email", item)
            self.assertIn("status", item)
            self.assertIn("created", item)
            self.assertIn("updated", item)
            self.assertIn("nickname", item)
            self.assertIn("image", item)
            self.assertIn("@controls", item)
            self.assertIn("self", item["@controls"])
            self.assertIn("href", item["@controls"]["self"])
			# extract id using regular expression from
			# href = item["@controls"]["self"]["href"] i.e
			# href = '/items/{msg_id}/'
            href = item["@controls"]["self"]["href"]
            id = re.sub(r'\D', "", href)
            self.assertEquals(item["@controls"]["self"]["href"], resources.api.url_for(resources.User, userid=id, _external=False))
            
            #self.assertEquals(item["@controls"]["profile"]["href"], FORUM_USER_PROFILE)
			
    def test_get_users_mimetype(self):
        """
        Checks that GET Messages return correct status code and data format
        """
        print "("+self.test_get_users_mimetype.__name__+")", self.test_get_users_mimetype.__doc__

        #Check that I receive status code 200
        resp = self.client.get(self.url)
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASONJSON, CHIRRUP_USER_PROFILE))
						  
    def test_add_user(self):
        """
        Checks that the user is added correctly

        """
        print "("+self.test_add_user.__name__+")", self.test_add_user.__doc__

        # With a complete request
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.user_1_request)
                               )
        self.assertEquals(resp.status_code, 201)
        self.assertIn("Location", resp.headers)
        url = resp.headers["Location"]
        resp2 = self.client.get(url)
        self.assertEquals(resp2.status_code, 200)

        #With just mandaaory parameters
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.user_2_request)
                               )
        self.assertEquals(resp.status_code, 201)
        self.assertIn("Location", resp.headers)
        url = resp.headers["Location"]
        resp2 = self.client.get(url)
        self.assertEquals(resp2.status_code, 200)
        
		# existing username
        resp3 = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.user_existing_username)
                               )
        self.assertEquals(resp3.status_code, 409)
        
		# existing email
        resp4 = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.user_existing_email)
                               )
        self.assertEquals(resp4.status_code, 409)
        
		# existing nickname
        resp5 = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.user_existing_nickname)
                               )
        self.assertEquals(resp5.status_code, 409)
		
    def test_add_user_with_missing_username(self):
        """
        Testing that trying to add a user with missing username will fail

        """
        print "("+self.test_add_user_with_missing_username.__name__+")", self.test_add_user_with_missing_username.__doc__
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.user_missing_username)
								)
        self.assertEquals(resp.status_code, 400)
		
    def test_add_user_with_missing_nickname(self):
        """
        Testing that trying to add a user with missing nickname will fail

        """
        print "("+self.test_add_user_with_missing_nickname.__name__+")", self.test_add_user_with_missing_nickname.__doc__
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.user_missing_nickname)
								)
        self.assertEquals(resp.status_code, 400)
		
    def test_add_user_with_missing_email(self):
        """
        Testing that trying to add a user with missing email will fail

        """
        print "("+self.test_add_user_with_missing_email.__name__+")", self.test_add_user_with_missing_email.__doc__
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.user_missing_email)
								)
        self.assertEquals(resp.status_code, 400)

    def test_wrong_type(self):
        """
        Test that return adequate error if sent incorrect mime type
        """
        print "("+self.test_wrong_type.__name__+")", self.test_wrong_type.__doc__
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": "text/html"},
                                data=json.dumps(self.user_1_request)
                               )
        self.assertEquals(resp.status_code, 415)
		
class UserTestCase (ResourcesAPITestCase):

    USER_ID_1 = 1
    USER_ID_2 = 20000
    USER_ID_3 = 3

    modify_user_1_request = {
        "nickname": "modifiedtestuser1",
        "image": "image1.jpg"
    }

    modify_user_2_request = {
        "nickname": "modifiedtestuser2"
    }
	
	#Missing nickname
    modify_user_missing_nickname = {
        "image": "image1.jpg"
    }

    def setUp(self):
        super(UserTestCase, self).setUp()
        self.url1 = resources.api.url_for(resources.User,
                                          userid=self.USER_ID_1,
                                          _external=False)
        self.url_wrong = resources.api.url_for(resources.User,
                                               userid=self.USER_ID_2,
                                               _external=False)
        self.url3 = resources.api.url_for(resources.User,
                                               userid=self.USER_ID_3,
                                               _external=False)
    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        #NOTE: self.shortDescription() shuould work.
        print "("+self.test_url.__name__+")", self.test_url.__doc__
        with resources.app.test_request_context(self.url1):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User)
			
    def test_get_user(self):
        """
        Checks that GET User returns correct status code and data format
        """
        print "(" + self.test_get_user.__name__ + ")", self.test_get_user.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url1)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            controls = data["@controls"]
            self.assertIn("private-data", controls)
            self.assertIn("delete", controls)

            # Check self-control
            self.assertIn("title", controls["private-data"])
            self.assertIn("href", controls["private-data"])
            self.assertIn("method", controls["private-data"])
            self.assertIn("encoding", controls["private-data"])

            # Check collection url
            users_info = data["users-info"]
            self.assertIn("user_id", users_info)
            self.assertIn("username", users_info)
            self.assertIn("email", users_info)
            self.assertIn("status", users_info)
            self.assertIn("created", users_info)
            self.assertIn("updated", users_info)
            self.assertIn("nickname", users_info)
            self.assertIn("image", users_info)
		
    def test_modify_user_with_missing_nickname(self):
        """
        Testing that trying to modify a user with missing nickname will fail

        """
        print "("+self.test_modify_user_with_missing_nickname.__name__+")", self.test_modify_user_with_missing_nickname.__doc__
        resp = self.client.put(resources.api.url_for(resources.User, userid=1),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.modify_user_missing_nickname)
                               )
        self.assertEquals(resp.status_code, 400)
		
    def test_wrong_type(self):
        """
        Test that return adequate error if sent incorrect mime type
        """
        print "("+self.test_wrong_type.__name__+")", self.test_wrong_type.__doc__
        resp = self.client.put(resources.api.url_for(resources.User, userid=1),
                                headers={"Content-Type": "text/html"},
                                data=json.dumps(self.modify_user_1_request)
                               )
        self.assertEquals(resp.status_code, 415)
			
    def test_modify_user(self):
        """
        Checks that Modify User return correct status code if modified
        """
        print "("+self.test_modify_user.__name__+")", self.test_modify_user.__doc__
        
        # With a complete request
        resp = self.client.put(resources.api.url_for(resources.User, userid=self.USER_ID_1),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.modify_user_1_request)
                               )
        self.assertEquals(resp.status_code, 204)
        
        # With just mandaaory parameters
        resp2 = self.client.put(resources.api.url_for(resources.User, userid=self.USER_ID_3),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.modify_user_2_request)
                               )
        self.assertEquals(resp2.status_code, 204)
			
    def test_delete_user(self):
        """
        Checks that Delete User return correct status code if corrected delete
        """
        print "("+self.test_delete_user.__name__+")", self.test_delete_user.__doc__
        resp = self.client.delete(self.url3)
        self.assertEquals(resp.status_code, 204)
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)
		
class MessagesTestCase (ResourcesAPITestCase): 

    ROOM_ID = 1
    ROOM_ID_WRONG = 2000
    url = '/rooms/{}/messages/'.format(ROOM_ID)   

    #Existing user
    message_for_exiting_user = {
        "content": "Hypermedia course",
        "sender": 1   
    }
	
    #Non existing user
    message_for_non_exiting_user = {
        "content": "Hypermedia course",
        "sender": 200   
    }

    #Missing the sender
    message_for_missing_sender = {
        "content": "Do you know any good online hypermedia course?"
    }

    #Missing the content
    message_for_missing_content = {
        "sender": 1
    }

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        #NOTE: self.shortDescription() shuould work.
        print "("+self.test_url.__name__+")", self.test_url.__doc__,
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Messages)
            
    def test_get_messages(self):
        """
        Checks that GET Messages return correct status code and data format
        """
        print "("+self.test_get_messages.__name__+")", self.test_get_messages.__doc__

        #Check that I receive status code 200
        resp = self.client.get(resources.api.url_for(resources.Messages, roomid=self.ROOM_ID))
        self.assertEquals(resp.status_code, 200)

        # Check that I receive a collection and adequate href
        data = json.loads(resp.data)
        
        #Check controls
        controls = data["@controls"]
        self.assertIn("self", controls)

        self.assertIn("href", controls["self"])
        self.assertEquals(controls["self"]["href"], self.url)

        #Check that items are correct.
        items = data["rooms"]
        #self.assertEquals(len(items), initial_messages)
        for item in items:
            self.assertIn("content", item)
            self.assertIn("sender", item)
            self.assertIn("timestamp", item)
            self.assertIn("@controls", item)
            self.assertIn("self", item["@controls"])
            self.assertIn("href", item["@controls"]["self"])
			# extract id using regular expression from
			# href = item["@controls"]["self"]["href"] i.e
			# href = '/items/{msg_id}/'
            href = item["@controls"]["self"]["href"]
            msg_id = re.sub(r'\D', "", href)
            self.assertEquals(item["@controls"]["self"]["href"], resources.api.url_for(resources.Message, messageid=msg_id, _external=False))

    def test_get_messages_mimetype(self):
        """
        Checks that GET Messages return correct status code and data format
        """
        print "("+self.test_get_messages_mimetype.__name__+")", self.test_get_messages_mimetype.__doc__

        #Check that I receive status code 200
        resp = self.client.get(flask.url_for("messages", roomid=self.ROOM_ID))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASONJSON, CHIRRUP_MESSAGE_PROFILE))
    
    def test_add_message(self):
        """
        Test adding messages to the database.
        """
        print "("+self.test_add_message.__name__+")", self.test_add_message.__doc__

		# Non existing room
        resp = self.client.post(resources.api.url_for(resources.Messages, roomid=self.ROOM_ID_WRONG),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.message_for_exiting_user)
                               )
        self.assertTrue(resp.status_code == 409)

		# Non existing user
        resp = self.client.post(resources.api.url_for(resources.Messages, roomid=self.ROOM_ID),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.message_for_non_exiting_user)
                               )
        self.assertTrue(resp.status_code == 409)

		# Existing user
        resp = self.client.post(resources.api.url_for(resources.Messages, roomid=self.ROOM_ID),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.message_for_exiting_user)
                               )
        self.assertTrue(resp.status_code == 201)
        url = resp.headers.get("Location")
        self.assertIsNotNone(url)
        resp = self.client.get(url)
        self.assertTrue(resp.status_code == 200)	

    def test_add_message_wrong_media(self):
        """
        Test adding messages with a media different than json
        """
        print "("+self.test_add_message_wrong_media.__name__+")", self.test_add_message_wrong_media.__doc__
		
        resp = self.client.post(resources.api.url_for(resources.Messages, roomid=self.ROOM_ID),
                                headers={"Content-Type": "text"},
                                data=self.message_for_exiting_user.__str__()
                               )
        self.assertTrue(resp.status_code == 415)

    def test_add_message_incorrect_format(self):
        """
        Test that add message response correctly when sending erroneous message
        format.
        """
        print "("+self.test_add_message_incorrect_format.__name__+")", self.test_add_message_incorrect_format.__doc__

		# Missing the sender
        resp = self.client.post(resources.api.url_for(resources.Messages, roomid=self.ROOM_ID),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.message_for_missing_sender)
                               )
        self.assertTrue(resp.status_code == 400)

		# Missing the content
        resp = self.client.post(resources.api.url_for(resources.Messages, roomid=self.ROOM_ID),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.message_for_missing_content)
                               )
        self.assertTrue(resp.status_code == 400)

class MessageTestCase (ResourcesAPITestCase):

    MESSAGE_ID = 1
    MESSAGE_ID_WRONG = 2000

    def setUp(self):
        super(MessageTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Message,
                                         messageid=self.MESSAGE_ID,
                                         _external=False)
        self.url_wrong = resources.api.url_for(resources.Message,
                                               messageid=self.MESSAGE_ID_WRONG,
                                               _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        #NOTE: self.shortDescription() shuould work.
        print "("+self.test_url.__name__+")", self.test_url.__doc__
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Message)

    def test_wrong_url(self):
        """
        Checks that GET Message return correct status code if given a
        wrong message
        """
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)
		
    def test_get_message(self):
        """
        Checks that GET Message return correct status code and data format
        """
        print "("+self.test_get_message.__name__+")", self.test_get_message.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            controls = data["@controls"]
                        
            #Check rest attributes
            messages_info = data["messages-info"]
            self.assertIn("message_id", messages_info)
            self.assertIn("room_id", messages_info)
            self.assertIn("sender", messages_info)
            self.assertIn("content", messages_info)
            self.assertIn("created", messages_info)
            self.assertIn("self", messages_info["@controls"])
            self.assertIn("href", messages_info["@controls"]["self"])
		
    def test_get_message_mimetype(self):
        """
        Checks that GET Messages return correct status code and data format
        """
        print "("+self.test_get_message_mimetype.__name__+")", self.test_get_message_mimetype.__doc__

        #Check that I receive status code 200
        resp = self.client.get(self.url)
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers.get("Content-Type", None),
                          "{};{}".format(MASONJSON, CHIRRUP_MESSAGE_PROFILE))
						  
    def test_delete_message(self):
        """
        Checks that Delete Message return correct status code if corrected delete
        """
        print "("+self.test_delete_message.__name__+")", self.test_delete_message.__doc__
        resp = self.client.delete(self.url)
        self.assertEquals(resp.status_code, 204)
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 404)

    def test_delete_nonexisting_message(self):
        """
        Checks that Delete Message return correct status code if given a wrong address
        """
        print "("+self.test_delete_nonexisting_message.__name__+")", self.test_delete_nonexisting_message.__doc__
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)

class RoomsTestCase (ResourcesAPITestCase):

	# add this as new & existing
    add_room_1_request = {
        "name" : "testroom1",
        "admin" : 5,
        "type" : "PUBLIC"
	}

	# add this as new & existing
    add_room_2_request = {
        "name" : "testroom2",
        "admin" : 5,
        "type" : "PRIVATE"
	}

	# missing name
    add_room_with_missing_name_request = {
        "admin" : 5,
        "type" : "PUBLIC"
	}

	# missing admin
    add_room_with_missing_admin_request = {
        "name" : "testroom3",
        "type" : "PUBLIC"
	}

	# missing type
    add_room_with_missing_type_request = {
        "name" : "testroom3",
        "admin" : 5
	}

	# invalid type
    add_room_with_invalid_type_request = {
        "name" : "testroom3",
        "admin" : 5,
		"type" : "UNKNOWN"
	}

	# non existing admin
    add_room_with_non_existing_admin_request = {
        "name" : "testroom3",
        "admin" : 50000000,
		"type": "PUBLIC"
	}
	
    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        #NOTE: self.shortDescription() shuould work.
        print "("+self.test_url.__name__+")", self.test_url.__doc__,
        with resources.app.test_request_context(flask.url_for("rooms")):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Rooms)
			
    def test_get_rooms_mimetype(self):
        """
        Checks that GET Rooms return correct status code and data format
        """
        print "("+self.test_get_rooms_mimetype.__name__+")", self.test_get_rooms_mimetype.__doc__

        #Check that I receive status code 200
        resp = self.client.get(flask.url_for("rooms"))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASONJSON, CHIRRUP_ROOM_PROFILE))
            
    def test_get_rooms(self):
        """
        Checks that GET Messages return correct status code and data format
        """
        print "("+self.test_get_rooms.__name__+")", self.test_get_rooms.__doc__

        #Check that I receive status code 200
        resp = self.client.get(flask.url_for("rooms"))
        self.assertEquals(resp.status_code, 200)

        # Check that I receive a collection and adequate href
        data = json.loads(resp.data)
        
        #Check controls
        controls = data["@controls"]
        self.assertIn("self", controls)
        self.assertIn("add-room", controls)

        self.assertIn("href", controls["self"])
        self.assertEquals(controls["self"]["href"], resources.api.url_for(resources.Rooms, _external=False))

        self.assertIn("href", controls["add-room"])
        self.assertEquals(controls["add-room"]["href"], resources.api.url_for(resources.Rooms, _external=False))

        self.assertIn("method", controls["add-room"])
        self.assertEquals(controls["add-room"]["method"], "POST")

        #Check that items are correct.
        items = data["rooms-all"]
        #self.assertEquals(len(items), initial_messages)
        for item in items:
            self.assertIn("room_id", item)
            self.assertIn("name", item)
            self.assertIn("admin", item)
            self.assertIn("created", item)
            self.assertIn("updated", item)
            self.assertIn("@controls", item)
            self.assertIn("self", item["@controls"])
            self.assertIn("href", item["@controls"]["self"])
			# extract id using regular expression from
			# href = item["@controls"]["self"]["href"] i.e
			# href = '/items/{msg_id}/'
            href = item["@controls"]["self"]["href"]
            id = re.sub(r'\D', "", href)
            self.assertEquals(href, resources.api.url_for(resources.Room, roomid=id, _external=False))
		
    def test_wrong_media_type(self):
        """
        Test that return adequate error if sent incorrect media type
        """
        print "("+self.test_wrong_media_type.__name__+")", self.test_wrong_media_type.__doc__
		
        resp = self.client.post(resources.api.url_for(resources.Rooms),
                                headers={"Content-Type": "text/html"},
                                data=json.dumps(self.add_room_1_request)
                               )
        self.assertEquals(resp.status_code, 415)
		
    def test_add_room(self):
        """
        Checks that the room is added correctly
        """
        print "("+self.test_add_room.__name__+")", self.test_add_room.__doc__

        # With a complete request
        resp = self.client.post(resources.api.url_for(resources.Rooms),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.add_room_1_request)
                               )
        self.assertEquals(resp.status_code, 201)
        self.assertIn("Location", resp.headers)
        url = resp.headers["Location"]
        resp2 = self.client.get(url)
        self.assertEquals(resp2.status_code, 200)

        # With just mandaaory parameters
        resp = self.client.post(resources.api.url_for(resources.Rooms),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.add_room_2_request)
                               )
        self.assertEquals(resp.status_code, 201)
        self.assertIn("Location", resp.headers)
        url = resp.headers["Location"]
        resp2 = self.client.get(url)
        self.assertEquals(resp2.status_code, 200)
        
        '''
		# existing room name
        resp3 = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.add_room_1_request)
                               )
        self.assertEquals(resp3.status_code, 409)
        '''
		
    def test_add_room_with_missing_name(self):
        """
        Testing that trying to add a room with missing name will fail

        """
        print "("+self.test_add_room_with_missing_name.__name__+")", self.test_add_room_with_missing_name.__doc__
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.add_room_with_missing_name_request)
								)
        self.assertEquals(resp.status_code, 400)
		
    def test_add_room_with_missing_admin(self):
        """
        Testing that trying to add a room with missing admin will fail

        """
        print "("+self.test_add_room_with_missing_admin.__name__+")", self.test_add_room_with_missing_admin.__doc__
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.add_room_with_missing_admin_request)
								)
        self.assertEquals(resp.status_code, 400)
		
    def test_add_room_with_missing_type(self):
        """
        Testing that trying to add a room with missing type will fail

        """
        print "("+self.test_add_room_with_missing_type.__name__+")", self.test_add_room_with_missing_type.__doc__
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.add_room_with_missing_type_request)
								)
        self.assertEquals(resp.status_code, 400)
	
    '''	
    def test_add_room_with_invalid_type(self):
        """
        Testing that trying to add a room with invalid type will fail

        """
        print "("+self.test_add_room_with_invalid_type.__name__+")", self.test_add_room_with_invalid_type.__doc__
        
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.add_room_with_invalid_type_request)
								)
        self.assertEquals(resp.status_code, 409)
	'''

    '''
    def test_add_room_with_non_existing_admin(self):
        """
        Testing that trying to add a room with invalid type will fail

        """
        print "("+self.test_add_room_with_non_existing_admin.__name__+")", self.test_add_room_with_non_existing_admin.__doc__
        
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.add_room_with_non_existing_admin_request)
								)
        self.assertEquals(resp.status_code, 409)    
    '''
	
class RoomTestCase (ResourcesAPITestCase):

    ROOM_ID_1 = 1
    ROOM_ID_2 = 20000

    def setUp(self):
        super(RoomTestCase, self).setUp()
        self.url1 = resources.api.url_for(resources.Room,
                                          roomid=self.ROOM_ID_1,
                                          _external=False)
        self.url_wrong = resources.api.url_for(resources.Room,
                                               roomid=self.ROOM_ID_2,
                                               _external=False)
											   
    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        #NOTE: self.shortDescription() shuould work.
        print "("+self.test_url.__name__+")", self.test_url.__doc__	
        with resources.app.test_request_context(self.url1):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Room)

    def test_get_room(self):
        """
        Checks that GET Room returns correct status code and data format
        """
        print "(" + self.test_get_room.__name__ + ")", self.test_get_room.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url1)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            # Check collection url
            rooms_info = data["rooms-info"]
            self.assertIn("room_id", rooms_info)
            self.assertIn("name", rooms_info)
            self.assertIn("admin", rooms_info)
            self.assertIn("created", rooms_info)
            self.assertIn("updated", rooms_info)
            self.assertIn("updated", rooms_info)
			
			# rooms_info controls
			
            rooms_info_controls = rooms_info["@controls"]
            self.assertIn("self", rooms_info_controls)
            self.assertIn("href", rooms_info_controls["self"])
            self.assertIn("rooms", rooms_info_controls)
            self.assertIn("href", rooms_info_controls["rooms"])

    def test_delete_room(self):
        """
        Checks that Delete Room return correct status code if corrected delete
        """
        print "("+self.test_delete_room.__name__+")", self.test_delete_room.__doc__
        resp = self.client.delete(self.url1)
        self.assertEquals(resp.status_code, 204)
        resp2 = self.client.get(self.url1)
        self.assertEquals(resp2.status_code, 404)

    def test_delete_nonexisting_room(self):
        """
        Checks that Delete Room return correct status code if given a wrong address
        """
        print "("+self.test_delete_nonexisting_room.__name__+")", self.test_delete_nonexisting_room.__doc__
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)
	
class MembersTestCase (ResourcesAPITestCase):

    ROOM_ID_1 = 1
    ROOM_ID_2 = 20000

    def setUp(self):
        super(MembersTestCase, self).setUp()
        self.url1 = resources.api.url_for(resources.Members,
                                          roomid=self.ROOM_ID_1,
                                          _external=False)
        self.url_wrong = resources.api.url_for(resources.Members,
                                               roomid=self.ROOM_ID_2,
                                               _external=False)
											   
    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        #NOTE: self.shortDescription() shuould work.
        print "("+self.test_url.__name__+")", self.test_url.__doc__	
        with resources.app.test_request_context(self.url1):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Members)

    def test_get_room_members(self):
        """
        Checks that GET Members of a Room returns correct status code and data format
        """
        print "(" + self.test_get_room_members.__name__ + ")", self.test_get_room_members.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url1)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)
			
			# controls
            controls = data["@controls"]
            self.assertIn("self", controls)
            self.assertIn("href", controls["self"])

            # Check collection url
            room_members = data["room-members"]
            for room_member in room_members:
                self.assertIn("id", room_member)
                self.assertIn("room_id", room_member)
                self.assertIn("user_id", room_member)
                self.assertIn("joined", room_member)

    def test_get_nonexisting_room_members(self):
        """
        Checks that Delete Room return correct status code if not exists
        """
        print "("+self.test_get_nonexisting_room_members.__name__+")", self.test_get_nonexisting_room_members.__doc__
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)
	
	
if __name__ == "__main__":
    print "Start running tests"
    unittest.main()