'''
Created on 13.02.2014
Modified on 01.02.2016
Database interface testing for all users related methods.

A Message object is a dictionary which contains the following keys:
      - messageid: id of the message (int)
      - title: message's title
      - body: message's TEXT
      - timestamp: UNIX timestamp (long integer) that specifies when the
                   message was created.
      - replyto: The id of the parent message. String with the format
                   msg-{id}. Its value can be None.
      - sender: The nickname of the message's creator
      - editor: The nickname of the message's editor.

A messages' list has the following format:
[{'messageid':'', 'title':'', 'timestamp':, 'sender':''},
 {'messageid':'', 'title':'', 'timestamp':, 'sender':''}]

@author: ivan
'''

import sqlite3, unittest

from api import engine, connections

#Path to the database file, different from the deployment db
DB_PATH = 'db/chirrup_test.db'
ENGINE = engine.Engine(DB_PATH)


#CONSTANTS DEFINING DIFFERENT USERS AND USER PROPERTIES
MESSAGE1_ID = 1

MESSAGE1 = {'message_id': MESSAGE1_ID,
            'user_id': '1',
            'room_id': '1',
            'content': 'Hello1',
            'created': '1362017481'
            }

MESSAGE2_ID = 2

MESSAGE2 = {'message_id': MESSAGE2_ID,
            'user_id': '1',
            'room_id': '2',
            'content': 'Hi',
            'created': '1362017481'
            }

WRONG_MESSAGE_ID = 200

INITIAL_SIZE = 10


class MessageDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the Messages related methods.
    '''
    #INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        ''' Creates the database structure. Removes first any preexisting
            database file
        '''
        print "Testing ", cls.__name__
        ENGINE.remove_database()
        ENGINE.create_tables()

    @classmethod
    def tearDownClass(cls):
        '''Remove the testing database'''
        print "Testing ENDED for ", cls.__name__
        ENGINE.remove_database()

    def setUp(self):
        '''
        Populates the database
        '''
        #This method load the initial values from chirrup_data_dump.sql
        ENGINE.populate_tables()

        #Creates a Connection instance to use the API
        self.connection = ENGINE.connect()

    def tearDown(self):
        '''
        Close underlying connection and remove all records from database
        '''
        self.connection.close()
        ENGINE.clear()

    def test_messages_table_created(self):
        '''
        Checks that the table initially contains 10 messages (check
        chirrup_data_dump.sql). NOTE: Do not use Connection instance but
        call directly SQL.
        '''
        print '('+self.test_messages_table_created.__name__+')', \
                  self.test_messages_table_created.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM messages'
        #Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement
            cur.execute(query)
            messages = cur.fetchall()
            #Assert
            self.assertEquals(len(messages), INITIAL_SIZE)

    def test_create_message_object(self):
        '''
        Check that the method _create_message_object works return adequate
        values for the first database row. NOTE: Do not use Connection instance
        to extract data from database but call directly SQL.
        '''
        print '('+self.test_create_message_object.__name__+')', \
              self.test_create_message_object.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM messages WHERE message_id = 1'
        #Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement
            cur.execute(query)
            #Extrac the row
            row = cur.fetchone()
        #Test the method
        message = self.connection._create_message_object(row)
        self.assertDictContainsSubset(message, MESSAGE1)

    def test_get_message(self):
        '''
        Test get_message with id msg-1 and msg-10
        '''
        print '('+self.test_get_message.__name__+')', \
              self.test_get_message.__doc__
        #Test with an existing message
        message = self.connection.get_message(MESSAGE1_ID)
        self.assertDictContainsSubset(message, MESSAGE1)
        message = self.connection.get_message(MESSAGE2_ID)
        self.assertDictContainsSubset(message, MESSAGE2)

    def test_get_message_malformedid(self):
        '''
        Test get_message with id "msg-1" (malformed)
        '''
        print '('+self.test_get_message_malformedid.__name__+')', \
              self.test_get_message_malformedid.__doc__
        #Test with an existing message
        with self.assertRaises(ValueError):
            self.connection.get_message('msg-1')

    def test_get_message_noexistingid(self):
        '''
        Test get_message with msg-200 (no-existing)
        '''
        print '('+self.test_get_message_noexistingid.__name__+')',\
              self.test_get_message_noexistingid.__doc__
        #Test with an existing message
        message = self.connection.get_message(WRONG_MESSAGE_ID)
        self.assertIsNone(message)

    def test_get_messages(self):
        '''
        Test that get_messages work correctly
        '''
        print '('+self.test_get_messages.__name__+')', self.test_get_messages.__doc__
        messages = self.connection.get_messages()
        #Check that the size is correct
        self.assertEquals(len(messages), INITIAL_SIZE)
        #Iterate throug messages and check if the messages with MESSAGE1_ID and
        #MESSAGE2_ID are correct:
        for message in messages:
            if message['message_id'] == MESSAGE1_ID:
                self.assertEquals(len(message), 5)
                self.assertDictContainsSubset(message, MESSAGE1)
            elif message['message_id'] == MESSAGE2_ID:
                self.assertEquals(len(message), 5)
                self.assertDictContainsSubset(message, MESSAGE2)

    def test_get_messages_specific_room(self):
        '''
        Get all messages from room_id 1. Check that their ids are 1 and 2.
        '''
        print '('+self.test_get_messages_specific_room.__name__+')', \
              self.test_get_messages_specific_room.__doc__
        messages = self.connection.get_messages(room_id=1)
        self.assertEquals(len(messages), 2)
        #Messages id are 1 and 2
        for message in messages:
            self.assertIn(message['messageid'], ('1', '2'))
            self.assertNotIn(message['messageid'], ('100', '12312',
                                                    '5', '33'))

    def test_get_messages_length(self):
        '''
        Check that the number_of_messages  is working in get_messages
        '''
        # Two messages in room id 1
        print '('+self.test_get_messages_length.__name__+')',\
              self.test_get_messages_length.__doc__
        messages = self.connection.get_messages(room_id=1,
                                                number_of_messages=2)
        self.assertEquals(len(messages), 2)
        #Number of messages is 2
        messages = self.connection.get_messages(room_id=1, number_of_messages=1)
        self.assertEquals(len(messages), 1)

    def test_delete_message(self):
        '''
        Test that the message message is deleted
        '''
        print '('+self.test_delete_message.__name__+')', \
              self.test_delete_message.__doc__
        resp = self.connection.delete_message(MESSAGE1_ID)
        self.assertTrue(resp)
        #Check that the messages has been really deleted throug a get
        resp2 = self.connection.get_message(MESSAGE1_ID)
        self.assertIsNone(resp2)

    def test_delete_message_malformedid(self):
        '''
        Test that trying to delete message with id ='600' (string) raises an error
        '''
        print '('+self.test_delete_message_malformedid.__name__+')', \
              self.test_delete_message_malformedid.__doc__
        #Test with an existing message
        with self.assertRaises(ValueError):
            self.connection.delete_message('msg-1')


    def test_delete_message_noexistingid(self):
        '''
        Test delete_message with message_id 200 (no-existing)
        '''
        print '('+self.test_delete_message_noexistingid.__name__+')', \
              self.test_delete_message_noexistingid.__doc__
        #Test with an existing message
        resp = self.connection.delete_message(WRONG_MESSAGE_ID)
        self.assertFalse(resp)

    def test_create_message(self):
        '''
        Test that a new message can be created
        '''
        print '('+self.test_create_message.__name__+')',\
              self.test_create_message.__doc__
        message_id = self.connection.create_message(1, 1, 'Hello from the otter side.')
        self.assertIsNotNone(message_id)
        #Get the expected modified message
        new_message = {}
        new_message['room_id'] = '1'
        new_message['user_id'] = '1'
        new_message['content'] = 'Hello from the otter side.'

        #Check that the messages has been really modified through a get
        resp2 = self.connection.get_message(message_id)
        self.assertDictContainsSubset(new_message, resp2)
        #CHECK NOW NOT REGISTERED USER
        message_id = self.connection.create_message(1, 1000, 'lol_xD')
        self.assertIsNone(message_id)


    def test_not_contains_message(self):
        '''
        Check if the database does not contain messages with id 200

        '''
        print '('+self.test_contains_message.__name__+')', \
              self.test_contains_message.__doc__
        self.assertFalse(self.connection.contains_message(WRONG_MESSAGE_ID))

    def test_contains_message(self):
        '''
        Check if the database contains messages with id 1 and 2

        '''
        print '('+self.test_contains_message.__name__+')', \
              self.test_contains_message.__doc__
        self.assertTrue(self.connection.contains_message(MESSAGE1_ID))
        self.assertTrue(self.connection.contains_message(MESSAGE2_ID))

if __name__ == '__main__':
    print 'Start running message tests'
    unittest.main()
