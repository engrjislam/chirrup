'''
Based on University of Oulu's Programmable web project-course exercise 1
Homepage:
http://confluence.atlassian.virtues.fi/display/PWP/521260S+Programmable+Web+Project+%285cu%29+Home

Created on 11.07.2017

Database interface testing for all users related methods.

A Message object is a dictionary which contains the following keys in a string-format:
      - message_id: id of the message
      - room_id: the id of the room where the message was sent to
      - user_id: the id of the user who sent the message
      - content: the content of the message
      - created: UNIX timestamp (long integer) that specifies when the
                   message was created.

A messages' list consists of several message objects.

'''

import sqlite3
import unittest

from api import engine

# Path to the database file, different from the deployment db
DB_PATH = 'db/chirrup_test.db'
ENGINE = engine.Engine(DB_PATH)

# CONSTANTS DEFINING DIFFERENT USERS AND USER PROPERTIES
MESSAGE1_ID = 1

MESSAGE1 = {
    'message_id': str(MESSAGE1_ID),
    'room_id': '1',
    'user_id': '3',
    'content': 'Hello1',
    'created': '1362017481'
}

MESSAGE2_ID = 2

MESSAGE2 = {
    'message_id': str(MESSAGE2_ID),
    'room_id': '1',
    'user_id': '2',
    'content': 'Hi',
    'created': '1362017481'
}
# Paremeters in a dict to test create_message()
NEW_MESSAGE = {
    'room_id': '1',
    'user_id': '1',
    'content': 'Hello from the otter side.',
    'created': '907123490'
}
WRONG_MESSAGE_ID = 200
WRONG_ROOM_ID = 200
MESSAGES_IN_ROOM_1 = 2
INITIAL_SIZE = 10
# Parameters for get_messages()
NO_MESSAGES_BEFORE = 1362017481
NO_MESSAGES_AFTER = 1362017481


class MessageDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the Messages related methods.
    '''

    # INITIATION AND TEARDOWN METHODS
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
        # This method load the initial values from chirrup_data_dump.sql
        ENGINE.populate_tables()

        # Creates a Connection instance to use the API
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
        print '(' + self.test_messages_table_created.__name__ + ')', \
            self.test_messages_table_created.__doc__
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM messages'
        # Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            cur.execute(query)
            messages = cur.fetchall()
            # Assert
            self.assertEquals(len(messages), INITIAL_SIZE)

    def test_create_message_object(self):
        '''
        Check that the method _create_message_object works return adequate
        values for the first database row. NOTE: Do not use Connection instance
        to extract data from database but call directly SQL.
        '''
        print '(' + self.test_create_message_object.__name__ + ')', \
            self.test_create_message_object.__doc__
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM messages WHERE message_id = 1'
        # Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            cur.execute(query)
            # Extrac the row
            row = cur.fetchone()
        # Test the method
        message = self.connection._create_message_object(row)
        self.assertDictContainsSubset(message, MESSAGE1)

    def test_get_message(self):
        '''
        Test get_message with id 1 and 2
        '''
        print '(' + self.test_get_message.__name__ + ')', \
            self.test_get_message.__doc__
        # Test with an existing message
        message = self.connection.get_message(MESSAGE1_ID)
        self.assertDictContainsSubset(message, MESSAGE1)
        message = self.connection.get_message(MESSAGE2_ID)
        self.assertDictContainsSubset(message, MESSAGE2)

    def test_get_message_malformedid(self):
        '''
        Test get_message with id "msg-1" (malformed)
        '''
        print '(' + self.test_get_message_malformedid.__name__ + ')', \
            self.test_get_message_malformedid.__doc__
        # Test with an existing message
        with self.assertRaises(ValueError):
            self.connection.get_message('msg-1')

    def test_get_message_noexistingid(self):
        '''
        Test get_message with id 200 (no-existing)
        '''
        print '(' + self.test_get_message_noexistingid.__name__ + ')', \
            self.test_get_message_noexistingid.__doc__
        # Test with an existing message
        message = self.connection.get_message(WRONG_MESSAGE_ID)
        self.assertIsNone(message)

    def test_get_messages(self):
        '''
        Get all messages from room_id 1. Check that their ids are 1 and 2.
        '''
        print '(' + self.test_get_messages.__name__ + ')', \
            self.test_get_messages.__doc__
        messages = self.connection.get_messages(room_id=1)
        self.assertEquals(len(messages), MESSAGES_IN_ROOM_1)
        # Messages id are 1 and 2
        for message in messages:
            self.assertIn(message['message_id'], ('1', '2'))
            self.assertNotIn(message['message_id'], ('100', '12312',
                                                     '5', '33'))

    def test_get_messages_noexistingid(self):
        '''
        Check that get_messages returns None for noexisting room.
        '''
        print '(' + self.test_get_messages_noexistingid.__name__ + ')', \
            self.test_get_messages_noexistingid.__doc__
        messages = self.connection.get_messages(room_id=200)
        self.assertIsNone(messages)

    def test_get_messages_length(self):
        '''
        Check that the number_of_messages is working in get_messages
        '''
        # Two messages in room id 1
        print '(' + self.test_get_messages_length.__name__ + ')', \
            self.test_get_messages_length.__doc__
        messages = self.connection.get_messages(room_id=1,
                                                number_of_messages=2)
        self.assertEquals(len(messages), 2)
        # Number of messages is 2
        messages = self.connection.get_messages(room_id=1, number_of_messages=1)
        self.assertEquals(len(messages), 1)

    def test_get_messages_timestamp(self):
        '''
        Check that the before and after are working in get_messages.
        '''
        # Two messages in room id 1
        print '(' + self.test_get_messages_length.__name__ + ')', \
            self.test_get_messages_length.__doc__
        messages = self.connection.get_messages(room_id=1, before=NO_MESSAGES_BEFORE)
        self.assertIsNone(messages)
        messages = self.connection.get_messages(room_id=1, after=NO_MESSAGES_AFTER)
        self.assertIsNone(messages)

    def test_delete_message(self):
        '''
        Test that the intended message is deleted.
        '''
        print '(' + self.test_delete_message.__name__ + ')', \
            self.test_delete_message.__doc__
        resp = self.connection.delete_message(MESSAGE1_ID)
        self.assertTrue(resp)
        # Check that the messages has been really deleted through a get
        resp2 = self.connection.get_message(MESSAGE1_ID)
        self.assertIsNone(resp2)

    def test_delete_message_malformedid(self):
        '''
        Test that trying to delete message with id ='msg-600' raises an error.
        '''
        print '(' + self.test_delete_message_malformedid.__name__ + ')', \
            self.test_delete_message_malformedid.__doc__
        # Test with an existing message
        with self.assertRaises(ValueError):
            self.connection.delete_message('msg-600')

    def test_delete_message_noexistingid(self):
        '''
        Test delete_message with message_id 200 (no-existing)
        '''
        print '(' + self.test_delete_message_noexistingid.__name__ + ')', \
            self.test_delete_message_noexistingid.__doc__
        # Test with an existing message
        resp = self.connection.delete_message(WRONG_MESSAGE_ID)
        self.assertFalse(resp)

    def test_create_message(self):
        '''
        Test that a new message can be created.
        '''
        print '(' + self.test_create_message.__name__ + ')', \
            self.test_create_message.__doc__
        message_id = self.connection.create_message(NEW_MESSAGE['room_id'],
                                                    NEW_MESSAGE['user_id'],
                                                    NEW_MESSAGE['content'],
                                                    NEW_MESSAGE['created'])
        self.assertIsNotNone(message_id)
        # Check that the messages has been really modified through a get
        resp2 = self.connection.get_message(message_id)
        self.assertDictContainsSubset(NEW_MESSAGE, resp2)

    def test_contains_message(self):
        '''
        Check if the database contains messages with id 1 and 2
        '''
        print '(' + self.test_contains_message.__name__ + ')', \
            self.test_contains_message.__doc__
        self.assertTrue(self.connection.contains_message(MESSAGE1_ID))
        self.assertTrue(self.connection.contains_message(MESSAGE2_ID))

    def test_contains_message_noexistingid(self):
        '''
        Check if the database does not contain messages with id 200
        '''
        print '(' + self.test_contains_message_noexistingid.__name__ + ')', \
            self.test_contains_message_noexistingid.__doc__
        self.assertFalse(self.connection.contains_message(WRONG_MESSAGE_ID))


if __name__ == '__main__':
    print 'Start running message tests'
    unittest.main()
