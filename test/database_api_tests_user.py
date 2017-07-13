'''
Based on University of Oulu's Programmable web project-course exercise 1.
Homepage:
http://confluence.atlassian.virtues.fi/display/PWP/521260S+Programmable+Web+Project+%285cu%29+Home

Database interface testing for all users related methods.
The user has a data model represented by the following User dictionary:


'''
import unittest
import sqlite3
from api import engine

# Path to the database file, different from the deployment db
DB_PATH = 'db/chirrup_test.db'
ENGINE = engine.Engine(DB_PATH)

# CONSTANTS DEFINING DIFFERENT USERS AND USER PROPERTIES
USER1_NICKNAME = 'rICK'
USER1_USERNAME = 'ABC1'
USER1_ID = 1
USER1 = {
    'public_profile': {
        'nickname': USER1_NICKNAME,
        'image': 'rick.jpg'},
    'private_profile': {
        'username': USER1_USERNAME,
        'email': '1@gmail.com',
        'status': 'ACTIVE',
        'updated': 'NULL',
        'created': '1362017481'
    }
}
MODIFIED_USER1 = {
    'public_profile': {
        'nickname': USER1_NICKNAME,
        'image': 'new_rick.jpg'},
    'private_profile': {
        'username': USER1_USERNAME,
        'email': 'new_1@gmail.com',
        'status': 'ACTIVE',
        'updated': 'NULL',
        'created': '1362017481'
    },
}

USER2_NICKNAME = 'mORTY'
USER2_USERNAME = 'ABC5'
USER2_ID = 5
USER2 = {
    'public_profile': {
        'nickname': USER2_NICKNAME,
        'image': 'morty.jpg'},
    'private_profile': {
        'username': USER2_USERNAME,
        'email': '5@gmail.com',
        'status': 'ACTIVE',
        'updated': 'NULL',
        'created': '1362017481'
    },
}
# Valid at first, modified during the test
NEW_PLACEHOLDER_USER = {
    'public_profile': {
        'nickname': 'some_long_andrandom091247laall3',
        'image': 'new_rick.jpg'},
    'private_profile': {
        'username': '09182lkjha8235agfds',
        'email': '9017824lkjhasf98y3wq4@gmail.com',
        'status': 'INACTIVE',
        'updated': 'NULL',
        'created': '1362017481'
    }
}
NEW_VALID_USER = {
    'public_profile': {
        'nickname': 'some_long_andrandom091247laall3',
        'image': 'new_rick.jpg'},
    'private_profile': {
        'username': '09182lkjha8235agfds',
        'email': '9017824lkjhasf98y3wq4@gmail.com',
        'status': 'INACTIVE',
        'updated': 'NULL',
        'created': '1362017481'
    }
}
NEW_USER = {
    'public_profile': {
        'nickname': 'Birdperson',
        'image': 'worms.jpg'},
    'private_profile': {
        'username': 'birdperson1',
        'email': 'birdperson@gmail.com',
        'status': 'ACTIVE',
        'updated': 'NULL',
        'created': '1362017481'
    }
}
USER_WRONG_ID = 200
USER_WRONG_NICKNAME = 'Wubba Lubba Dub Dub'
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

    def test_users_table_created(self):
        '''
        Checks that the table initially contains 10 users (chirrup_data_dump.sql).
        NOTE: Do not use Connection instance but call directly SQL.
        '''
        print '(' + self.test_users_table_created.__name__ + ')', \
            self.test_users_table_created.__doc__
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM user'
        query2 = 'SELECT * FROM user_profile'
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
            users = cur.fetchall()
            # Assert
            self.assertEquals(len(users), INITIAL_SIZE)
            # Check the users_profile:
            cur.execute(query2)
            users = cur.fetchall()
            # Assert
            self.assertEquals(len(users), INITIAL_SIZE)

    def test_create_user_object(self):
        '''
        Check that the method create_user_object works return adequate values
        for the first database row. NOTE: Do not use Connection instance to
        extract data from database but call directly SQL.
        '''
        print '(' + self.test_create_user_object.__name__ + ')', \
            self.test_create_user_object.__doc__
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT user.*, user_profile.* FROM user, user_profile \
                 WHERE user.user_id = user_profile.user_id'
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
        user = self.connection._create_user_object(row)
        # update value not available, so it is added to MODIFIED_USER1
        user['private_profile']['updated'] = USER1['private_profile']['updated']
        self.assertDictContainsSubset(user, USER1)

    def test_get_user(self):
        '''
        Test get_user with id 1 and 5
        '''
        print '(' + self.test_get_user.__name__ + ')', \
            self.test_get_user.__doc__

        # Test with an existing user
        user = self.connection.get_user(USER1_ID)
        self.assertDictContainsSubset(user, USER1)
        user = self.connection.get_user(USER2_ID)
        self.assertDictContainsSubset(user, USER2)

    def test_get_user_noexisting_id(self):
        '''
        Test get_user with id 200/USER_WRONG_ID (no-existing)
        '''
        print '(' + self.test_get_user_noexisting_id.__name__ + ')', \
            self.test_get_user_noexisting_id.__doc__

        user = self.connection.get_user(USER_WRONG_ID)
        self.assertIsNone(user)

    def test_get_users(self):
        '''
        Test that get_users work correctly and extract required user info
        '''
        print '(' + self.test_get_users.__name__ + ')', \
            self.test_get_users.__doc__
        users = self.connection.get_users()
        # Check that the size is correct
        self.assertEquals(len(users), INITIAL_SIZE)
        # Iterate through users and check if the users with USER1_ID and
        # USER2_ID are correct:
        for user in users:
            if user['public_profile']['nickname'] == USER1_NICKNAME:
                self.assertDictContainsSubset(user['public_profile'], USER1['public_profile'])
            elif user['public_profile']['nickname'] == USER2_NICKNAME:
                self.assertDictContainsSubset(user['public_profile'], USER2['public_profile'])

    def test_delete_user(self):
        '''
        Test that the user with USER2_ID(5) is deleted. Admin users in room cannot be deleted.
        '''
        print '(' + self.test_delete_user.__name__ + ')', \
            self.test_delete_user.__doc__
        resp = self.connection.delete_user(USER2_ID)
        self.assertTrue(resp)
        # Check that user status is set to 'INACTIVE' through get
        resp2 = self.connection.get_user(USER2_ID)
        self.assertEquals(resp2['private_profile']['status'], 'INACTIVE')

    def test_delete_only_one_user(self):
        '''
        Test that ensures that only specified user is deleted
        '''
        print '(' + self.test_delete_only_one_user.__name__ + ')', \
            self.test_delete_only_one_user.__doc__


    def test_delete_user_noexisting_id(self):
        '''
        Test delete_user with user_id 200 (no-existing)
        '''
        print '(' + self.test_delete_user_noexisting_id.__name__ + ')', \
            self.test_delete_user_noexisting_id.__doc__
        # Test with an existing user
        resp = self.connection.delete_user(USER_WRONG_ID)
        self.assertFalse(resp)

    def test_modify_user(self):
        '''
        Test that the user with id 1 is modified.
        '''
        print '(' + self.test_modify_user.__name__ + ')', \
            self.test_modify_user.__doc__
        # Get the modified user
        resp = self.connection.modify_user(USER1_ID, MODIFIED_USER1)
        self.assertEquals(resp, USER1_ID)
        # Check that the users has been really modified through a get
        resp2 = self.connection.get_user(USER1_ID)
        resp_p_profile = resp2['public_profile']
        resp_r_profile = resp2['private_profile']
        # Check the expected values
        p_profile = MODIFIED_USER1['public_profile']
        r_profile = MODIFIED_USER1['private_profile']
        self.assertEquals(p_profile['nickname'], resp_p_profile['nickname'])
        self.assertEquals(p_profile['image'], resp_p_profile['image'])
        self.assertEquals(r_profile['username'], resp_r_profile['username'])
        self.assertEquals(r_profile['email'], resp_r_profile['email'])
        self.assertEquals(r_profile['status'], resp_r_profile['status'])
        self.assertEquals(r_profile['created'], resp_r_profile['created'])
        # update value not available, so it is added to MODIFIED_USER1
        MODIFIED_USER1['private_profile']['updated'] = resp_r_profile['updated']

        self.assertDictContainsSubset(resp2, MODIFIED_USER1)

    def test_modify_user_noexisting_id(self):
        '''
        Test modify_user with id 200 (no-existing)
        '''
        print '(' + self.test_modify_user_noexisting_id.__name__ + ')', \
            self.test_modify_user_noexisting_id.__doc__
        # Test with an existing user
        resp = self.connection.modify_user(USER_WRONG_ID, USER1)
        self.assertIsNone(resp)

    def test_append_user(self):
        # TODO returns none when appending a new user
        '''
        Test that new users can be added.
        '''
        print '(' + self.test_append_user.__name__ + ')', \
            self.test_append_user.__doc__
        user_id = self.connection.append_user(NEW_USER)
        self.assertIsNotNone(user_id)
        # Check that the user has been added through get
        resp2 = self.connection.get_user(user_id)
        # add the dates from resp2 to NEW_USER, cannot know the moment when the tests is run
        NEW_USER['private_profile']['created'] = NEW_USER['private_profile']['created']
        self.assertDictContainsSubset(NEW_USER['public_profile'],
                                      resp2['public_profile'])
        self.assertDictContainsSubset(NEW_USER['public_profile'],
                                      resp2['public_profile'])

    def test_append_existing_user(self):
        '''
        Test that two users cannot be added with the same username, nickname or email.
        NEW_PLACEHOLDER_USER first valid. It is corrupted by USER1 (existing user) values. After the test_case
        the non-existing NEW_PLACEHOLDER_USER value is restored.
        '''
        print '(' + self.test_append_existing_user.__name__ + ')', \
            self.test_append_existing_user.__doc__
        pr = 'private_profile'
        pu = 'public_profile'
        # username tests
        NEW_PLACEHOLDER_USER['private_profile']['username'] = USER1[pr]['username']
        user_id = self.connection.append_user(NEW_PLACEHOLDER_USER)
        self.assertFalse(user_id)
        NEW_PLACEHOLDER_USER[pr]['username'] = NEW_VALID_USER[pr]['username']
        # nickname tests
        NEW_PLACEHOLDER_USER[pu]['nickname'] = USER1[pu]['nickname']
        user_id = self.connection.append_user(NEW_PLACEHOLDER_USER)
        self.assertFalse(user_id)
        NEW_PLACEHOLDER_USER[pu]['nickname'] = NEW_VALID_USER[pu]['nickname']
        # email tests
        NEW_PLACEHOLDER_USER[pr]['email'] = USER1[pr]['email']
        user_id = self.connection.append_user(NEW_PLACEHOLDER_USER)
        self.assertFalse(user_id)
        NEW_PLACEHOLDER_USER[pr]['email'] = NEW_VALID_USER[pr]['email']

    def test_get_user_id(self):
        '''
        Test that get_user_id returns the right value given a nickname
        '''
        print '(' + self.test_get_user_id.__name__ + ')', \
            self.test_get_user_id.__doc__
        id = self.connection.get_user_id(USER1_NICKNAME)
        self.assertEquals(USER1_ID, id)
        id = self.connection.get_user_id(USER2_NICKNAME)
        self.assertEquals(USER2_ID, id)

    def test_get_user_nickname(self):
        '''
        Test that get_user_nickname returns the right value given a user_id
        '''
        print '(' + self.test_get_user_nickname.__name__ + ')', \
            self.test_get_user_nickname.__doc__
        id = self.connection.get_user_nickname(USER1_ID)
        self.assertEquals(USER1_NICKNAME, id)
        id = self.connection.get_user_nickname(USER2_ID)
        self.assertEquals(USER2_NICKNAME, id)

    def test_get_user_id_unknown_user(self):
        '''
        Test that get_user_id returns None when the nickname does not exist
        '''
        print '(' + self.test_get_user_id_unknown_user.__name__ + ')', \
            self.test_get_user_id_unknown_user.__doc__
        nickname = self.connection.get_user_id(USER_WRONG_NICKNAME)
        self.assertIsNone(nickname)

    def test_get_user_nickname_unknown_user(self):
        '''
        Test that get_user_nickname returns None when the user_id does not exist
        '''
        print '(' + self.test_get_user_nickname_unknown_user.__name__ + ')', \
            self.test_get_user_nickname_unknown_user.__doc__
        id = self.connection.get_user_nickname(USER_WRONG_ID)
        self.assertIsNone(id)

    def test_not_contains_user(self):
        '''
        Check if the database does not contain users with id 200
        '''
        print '(' + self.test_contains_user.__name__ + ')', \
            self.test_contains_user.__doc__
        self.assertFalse(self.connection.contains_user(USER_WRONG_ID))

    def test_contains_user(self):
        '''
        Check if the database contains users with id 1 and id 5
        '''
        print '(' + self.test_contains_user.__name__ + ')', \
            self.test_contains_user.__doc__
        self.assertTrue(self.connection.contains_user(USER1_ID))
        self.assertTrue(self.connection.contains_user(USER2_ID))


if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()
