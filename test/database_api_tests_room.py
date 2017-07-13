'''
Based on University of Oulu's Programmable web project-course exercise 1.
Homepage:
http://confluence.atlassian.virtues.fi/display/PWP/521260S+Programmable+Web+Project+%285cu%29+Home

Database interface testing for all rooms related methods.
The room has a data model represented by the following User dictionary:


'''
import unittest
import sqlite3
from api import engine

# Path to the database file, different from the deployment db
DB_PATH = 'db/chirrup_test.db'
ENGINE = engine.Engine(DB_PATH)
# CONSTANTS DEFINING DIFFERENT USERS AND USER PROPERTIES
ROOM1_NAME = 'room1'
ROOM1_ID = 1
ROOM1 = {
    'name': ROOM1_NAME,
    'type': 'PRIVATE',
    'admin': '1',
    'status': 'ACTIVE',
    'created': '1362017481',
    'updated': 'NULL'
}
MODIFIED_ROOM1 = {
    'name': ROOM1_NAME,
    'type': 'PRIVATE',
    'admin': '5',
    'status': 'ACTIVE',
    'created': '1362017481',
    'updated': 'NULL'
}
ROOM2_NAME = 'room5'
ROOM2_ID = 5
ROOM2 = {
    'name': ROOM2_NAME,
    'type': 'PUBLIC',
    'admin': '5',
    'status': 'ACTIVE',
    'created': '1362017481',
    'updated': 'NULL'
}
# Valid at first, modified during the test
NEW_PLACEHOLDER_ROOM = {
    'name': ROOM1_NAME,
    'type': 'PRIVATE',
    'admin': '1',
    'status': 'ACTIVE',
    'created': '1362017481',
    'updated': 'NULL'
}
NEW_VALID_ROOM = {
    'name': ROOM2_NAME,
    'type': 'PUBLIC',
    'admin': '5',
    'status': 'ACTIVE',
    'created': '1362017481',
    'updated': 'NULL'
}
NEW_ROOM = {
    'name': 'some_room',
    'type': 'PUBLIC',
    'admin': '7'
}
ROOM_WRONG_ID = 200
ROOM_WRONG_NAME = 'Wubba Lubba Dub Dub'
INITIAL_SIZE = 10


class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the Users related methods.
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
        # This method load the initial values from forum_data_dump.sql
        ENGINE.populate_tables()
        # Creates a Connection instance to use the API
        self.connection = ENGINE.connect()

    def tearDown(self):
        '''
        Close underlying connection and remove all records from database
        '''
        self.connection.close()
        ENGINE.clear()

    def test_room_tables_created(self):
        '''
        Checks that the room table initially contains 10 rooms room_users table 10 room members.
        Defined in chirrup_data_dump.sql.
        NOTE: Do not use Connection instance but call directly SQL.
        '''
        print '(' + self.test_room_tables_created.__name__ + ')', \
            self.test_room_tables_created.__doc__
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM room'
        query2 = 'SELECT * FROM room_users'
        # Connects to the database.
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            cur.execute(query1)
            rooms = cur.fetchall()
            # Assert
            self.assertEquals(len(rooms), INITIAL_SIZE)
            # Check the rooms_profile:
            cur.execute(query2)
            rooms = cur.fetchall()
            # Assert
            self.assertEquals(len(rooms), INITIAL_SIZE)

    def test_create_room_object(self):
        '''
        Check that the method _create_room_object works return adequate values
        for the first database row. NOTE: Do not use Connection instance to
        extract data from database but call directly SQL.
        '''
        print '(' + self.test_create_room_object.__name__ + ')', \
            self.test_create_room_object.__doc__
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM room WHERE room_id = 1'
        # Get the sqlite3 con from the Connection instance
        con = self.connection.con
        # I am doing operations after with, so I must explicitly close the
        # the connection to be sure that no locks are kepts. The with, close
        # the connection when it has gone out of scope
        # try:
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            cur.execute(query)
            # Extract the row
            row = cur.fetchone()
            # finally:
        #    con.close()
        # Test the method
        room = self.connection._create_room_object(row)
        # update value cannot be known initially, so it is overwritten
        room['updated'] = ROOM1['updated']
        self.assertDictContainsSubset(room, ROOM1)

    def test_get_room(self):
        '''
        Test get_room with id 1 and 5
        '''
        print '(' + self.test_get_room.__name__ + ')', \
            self.test_get_room.__doc__

        # Test with an existing room
        room = self.connection.get_room(ROOM1_ID)
        self.assertDictContainsSubset(room, ROOM1)
        room = self.connection.get_room(ROOM2_ID)
        self.assertDictContainsSubset(room, ROOM2)

    def test_get_room_noexisting_id(self):
        '''
        Test get_room with id 200/ROOM_WRONG_ID (no-existing)
        '''
        print '(' + self.test_get_room_noexisting_id.__name__ + ')', \
            self.test_get_room_noexisting_id.__doc__

        room = self.connection.get_room(ROOM_WRONG_ID)
        self.assertIsNone(room)

    def test_get_rooms(self):
        '''
        Test that get_rooms work correctly and extract required room info
        '''
        print '(' + self.test_get_rooms.__name__ + ')', \
            self.test_get_rooms.__doc__
        rooms = self.connection.get_rooms()
        # Check that the size is correct
        self.assertEquals(len(rooms), INITIAL_SIZE)
        # Iterate through rooms and check if the rooms with ROOM1_ID and
        # ROOM2_ID are correct:
        for rooms in rooms:
            if rooms['name'] == ROOM1_NAME:
                self.assertDictContainsSubset(rooms['public_profile'], ROOM1['public_profile'])
            elif rooms['public_profile']['nickname'] == ROOM2_NAME:
                self.assertDictContainsSubset(rooms['public_profile'], ROOM2['public_profile'])

    def test_delete_room(self):
        '''
        Test that the room with ROOM2_ID(5) is deleted. Admin rooms in room cannot be deleted.
        '''
        print '(' + self.test_delete_room.__name__ + ')', \
            self.test_delete_room.__doc__
        resp = self.connection.delete_room(ROOM2_ID)
        self.assertTrue(resp)
        # Check that room status is set to 'INACTIVE' through get
        resp2 = self.connection.get_room(ROOM2_ID)
        self.assertEquals(resp2['private_profile']['status'], 'INACTIVE')

    def test_delete_only_one_room(self):
        '''
        Test that ensures that only specified room is deleted
        '''
        print '(' + self.test_delete_only_one_room.__name__ + ')', \
            self.test_delete_only_one_room.__doc__


    def test_delete_room_noexisting_id(self):
        '''
        Test delete_room with room_id 200 (no-existing)
        '''
        print '(' + self.test_delete_room_noexisting_id.__name__ + ')', \
            self.test_delete_room_noexisting_id.__doc__
        # Test with an existing room
        resp = self.connection.delete_room(ROOM_WRONG_ID)
        self.assertFalse(resp)

    def test_modify_room(self):
        '''
        Test that the room with id 1 is modified.
        '''
        print '(' + self.test_modify_room.__name__ + ')', \
            self.test_modify_room.__doc__
        # Get the modified room
        resp = self.connection.modify_room(ROOM1_ID, MODIFIED_ROOM1)
        self.assertEquals(resp, ROOM1_ID)
        # Check that the rooms has been really modified through a get
        resp2 = self.connection.get_room(ROOM1_ID)
        resp_p_profile = resp2['public_profile']
        resp_r_profile = resp2['private_profile']
        # Check the expected values
        p_profile = MODIFIED_ROOM1['public_profile']
        r_profile = MODIFIED_ROOM1['private_profile']
        self.assertEquals(p_profile['nickname'], resp_p_profile['nickname'])
        self.assertEquals(p_profile['image'], resp_p_profile['image'])
        self.assertEquals(r_profile['roomname'], resp_r_profile['roomname'])
        self.assertEquals(r_profile['email'], resp_r_profile['email'])
        self.assertEquals(r_profile['status'], resp_r_profile['status'])
        self.assertEquals(r_profile['created'], resp_r_profile['created'])
        # update value not available, so it is added to MODIFIED_ROOM1
        MODIFIED_ROOM1['private_profile']['updated'] = resp_r_profile['updated']

        self.assertDictContainsSubset(resp2, MODIFIED_ROOM1)

    def test_modify_room_noexisting_id(self):
        '''
        Test modify_room with id 200 (no-existing)
        '''
        print '(' + self.test_modify_room_noexisting_id.__name__ + ')', \
            self.test_modify_room_noexisting_id.__doc__
        # Test with an existing room
        resp = self.connection.modify_room(ROOM_WRONG_ID, ROOM1)
        self.assertIsNone(resp)

    def test_create_room(self):
        # TODO returns none when creating a new room
        '''
        Test that new rooms can be added.
        '''
        print '(' + self.test_create_room.__name__ + ')', \
            self.test_create_room.__doc__
        room_id = self.connection.create_room(NEW_ROOM)
        self.assertIsNotNone(room_id)
        # Check that the room has been added through get
        resp2 = self.connection.get_room(room_id)
        self.assertDictContainsSubset(NEW_ROOM, resp2)
        self.assertDictContainsSubset(NEW_ROOM, resp2)

    def test_create_existing_room(self):
        '''
        Test that two rooms cannot be added with the same name.
        NEW_PLACEHOLDER_ROOM first valid. It is corrupted by ROOM1 (existing room) values. After the test_case
        the non-existing NEW_PLACEHOLDER_ROOM value is restored.
        '''
        print '(' + self.test_create_existing_room.__name__ + ')', \
            self.test_create_existing_room.__doc__
        # name tests
        NEW_PLACEHOLDER_ROOM['name'] = ROOM1['name']
        room_id = self.connection.create_room(NEW_PLACEHOLDER_ROOM)
        self.assertFalse(room_id)
        NEW_PLACEHOLDER_ROOM['name'] = NEW_VALID_ROOM['name']

    def test_get_room_id(self):
        '''
        Test that get_room_id returns the right value given a name
        '''
        print '(' + self.test_get_room_id.__name__ + ')', \
            self.test_get_room_id.__doc__
        id = self.connection.get_room_id(ROOM1_NAME)
        self.assertEquals(ROOM1_ID, id)
        id = self.connection.get_room_id(ROOM2_NAME)
        self.assertEquals(ROOM2_ID, id)

    def test_get_room_name(self):
        '''
        Test that get_room_name returns the right value given a room_id
        '''
        print '(' + self.test_get_room_name.__name__ + ')', \
            self.test_get_room_name.__doc__
        id = self.connection.get_room_name(ROOM1_ID)
        self.assertEquals(ROOM1_NAME, id)
        id = self.connection.get_room_name(ROOM2_ID)
        self.assertEquals(ROOM2_NAME, id)

    def test_get_room_id_unknown_room(self):
        '''
        Test that get_room_id returns None when the nickname does not exist
        '''
        print '(' + self.test_get_room_id_unknown_room.__name__ + ')', \
            self.test_get_room_id_unknown_room.__doc__
        nickname = self.connection.get_room_id(ROOM_WRONG_NAME)
        self.assertIsNone(nickname)

    def test_get_room_name_unknown_room(self):
        '''
        Test that get_room_name returns None when the room_id does not exist
        '''
        print '(' + self.test_get_room_name_unknown_room.__name__ + ')', \
            self.test_get_room_name_unknown_room.__doc__
        id = self.connection.get_room_name(ROOM_WRONG_ID)
        self.assertIsNone(id)

    def test_not_contains_room(self):
        '''
        Check if the database does not contain rooms with id 200
        '''
        print '(' + self.test_contains_room.__name__ + ')', \
            self.test_contains_room.__doc__
        self.assertFalse(self.connection.contains_room(ROOM_WRONG_ID))

    def test_contains_room(self):
        '''
        Check if the database contains rooms with id 1 and id 5
        '''
        print '(' + self.test_contains_room.__name__ + ')', \
            self.test_contains_room.__doc__
        self.assertTrue(self.connection.contains_room(ROOM1_ID))
        self.assertTrue(self.connection.contains_room(ROOM2_ID))


if __name__ == '__main__':
    print 'Start running room tests'
    unittest.main()
