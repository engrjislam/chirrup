'''
Programmable Web Project course exercise 1 database.py used as a template for implementation

Created on 11.07.2017
'''

from datetime import datetime
import time, sqlite3


class Connection(object):
    '''
    API to access the Chirrup database.

    The sqlite3 connection instance is accessible to all the methods of this
    class through the :py:attr:`self.con` attribute.

    An instance of this class should not be instantiated directly using the
    constructor. Instead use the :py:meth:`Engine.connect`.

    Use the method :py:meth:`close` in order to close a connection.
    A :py:class:`Connection` **MUST** always be closed once when it is not going to be
    utilized anymore in order to release internal locks.

    :param db_path: Location of the database file.
    :type dbpath: str

    '''
    def __init__(self, db_path):
        super(Connection, self).__init__()
        self.con = sqlite3.connect(db_path)

    def close(self):
        '''
        Closes the database connection, commiting all changes.

        '''
        if self.con:
            self.con.commit()
            self.con.close()

    #FOREIGN KEY STATUS
    def check_foreign_keys_status(self):
        '''
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.

        '''
        try:
            #Create a cursor to receive the database values
            cur = self.con.cursor()
            #Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            #We know we retrieve just one record: use fetchone()
            data = cur.fetchone()
            is_activated = data == (1,)
            print "Foreign Keys status: %s" % 'ON' if is_activated else 'OFF'
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            self.close()
            raise excp
        return is_activated

    def set_foreign_keys_support(self):
        '''
        Activate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, ON
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    def unset_foreign_keys_support(self):
        '''
        Deactivate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = OFF'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, OFF
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    #HELPERS
    #Here the helpers that transform database rows into dictionary. They work
    #similarly to ORM

    #Helpers for messages
    def _create_message_object(self, row):
        '''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``message_id``: id of the message.``.
            * ``room_id``: The room where the message was sent to.
            * ``user_id``: The user who sent the message
            * ``content``: message's text
            * ``created``: UNIX timestamp (long integer) that specifies when
              the message was created.

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        '''
        # values from the row converted to string from unicode string, from u'<string>' to '<string>'
        message_id = str(row['message_id'])
        message_room_id = str(row['room_id'])
        message_user_id = str(row['user_id'])
        message_created = str(row['created'])
        message_content = str(row['content'])

        message = {'message_id': message_id, 'room_id': message_room_id,
                   'user_id': message_user_id, 'created': message_created,
                   'content': message_content}
        return message

    #Helpers for users
    def _create_user_object(self, row):
        '''
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following format:

            .. code-block:: javascript

                {'public_profile':{'nickname':,'image':''},
                'restricted_profile':{'username':'','password':'','email':'',
                                      'status':'','created':'','updated':''}
                }

            where:

            * ``nickname``: nickname of the user
            * ``image``: name of the image file

            * ``username``: used for login
            * ``password``: used for login
            * ``email``: current email of the user, login and user contact purposes
            * ``status``: ACTIVE/INACTIVE, deleting a user sets this field INACTIVE.
            * ``created``: when the user account was created, UNIX timestamp when the user registered in the system (long integer)
            * ``updated``: when the user account was modified, UNIX timestamp when the user registered in the system (long integer)

            Note that all values are string if they are not otherwise indicated.

        '''
        return {'public_profile': {'nickname': str(row['nickname']),
                                   'image': str(row['image'])},
                'restricted_profile': {'username': str(row['username']),
                                       'password': str(row['password']),
                                       'email': str(row['email']),
                                       'status': str(row['status']),
                                       'created': str(row['created']),
                                       'updated': str(row['updated'])}
                }

    # lighter version of user object, probably not needed
    '''
    def _create_user_list_object(self, row):
        
        Same as :py:meth:`_create_message_object`. However, the resulting
        dictionary is targeted to build messages in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``registrationdate`` and
            ``nickname``

        
        return {'registrationdate': row['regDate'], 'nickname': row['nickname']}
    '''

    def _create_room_object(self, row):
        '''
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following keys:

            * ``name``: name of the room
            * ``type``: "PRIVATE" or "PUBLIC"
            * ``admin``: user_id of the user with admin privileges, initially given for the user who creates the room
            * ``status``: ACTIVE/INACTIVE, deleting a user sets this field INACTIVE.
            * ``created``: when the room was created, UNIX timestamp (long integer)
            * ``updated``: when the room information(name, type, admin, status) was modified, UNIX timestamp (long integer)

            Note that all values are string if they are not otherwise indicated.

        '''
        return {
            'name': str(row['name']),
            'type': str(row['type']),
            'admin': str(row['admin']),
            'status': str(row['status']),
            'created': str(row['created']),
            'updated': str(row['updated'])
        }

    #API ITSELF
    #Message Table API.
    def get_message(self, message_id):
        '''
        Extracts a message from the database.

        :param message_id: The id of the message.
        :type message_id: int
        :return: A dictionary with the format provided in
            :py:meth:`_create_message_object` or None if the message with target
            id does not exist.
        :raise ValueError if message_id malformed
        '''

        try:
            message_id = int(message_id)
        except:
            raise ValueError

        # Init
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        query = 'SELECT * FROM messages WHERE message_id = ?'

        # Execute the query
        pvalue = (message_id,)
        cur.execute(query, pvalue)
        #Process the response.
        #Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        #Build the return object
        return self._create_message_object(row)

    def get_messages(self, room_id, number_of_messages=-1,
                     before=-1, after=-1):
        '''
        Return a list of all the messages in the database filtered by the
        conditions provided in the parameters.

        :param room_id:  Search messages filtering with room_id.
        :type room_id: int
        :param number_of_messages: default -1. Sets the maximum number of
            messages returning in the list. If set to -1, there is no limit.
        :type number_of_messages: int
        :param before: All timestamps > ``before`` (UNIX timestamp) are removed.
            If set to -1, this condition is not applied.
        :type before: long
        :param after: All timestamps < ``after`` (UNIX timestamp) are removed.
            If set to -1, this condition is not applied.
        :type after: long

        :return: A list of messages. Each message is a dictionary containing
            the following keys:

            * ``message_id``: int
            * ``room_id``: room_id where the message was sent to.
            * ``user_id``: user_id of the message's author.
            * ``content``: string containing the title of the message.
            * ``created``: UNIX timestamp (long int) that specifies when the
                message was created.

            Note that all values in the returned dictionary are string unless
            otherwise stated.

            None is returned if the room_id doesn't exist.

        :raises ValueError: if ``before`` or ``after`` are not valid UNIX
            timestamps or ``before`` > ``after`` or arguments type is not int.
        :raises ValueError: if room_id not convertable to int.

        '''

        try:
            room_id = int(room_id)
        except:
            raise ValueError

        # Check input parameters
        if type(number_of_messages) is not int or type(before) is not int or type(after) is not int:
            raise ValueError

        if after > before:
            raise ValueError

        # Initialization
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # Check if message exists
        cur.execute('SELECT * from messages WHERE message_id = %s' % str(room_id))
        row = cur.fetchone()
        if row is None:
            return None

        # Create the SQL Statement build the string depending on the existence
        # of room_id, numbero_of_messages, before and after arguments.
        query = 'SELECT * FROM messages WHERE room_id=%s' % str(room_id)

        #Before restriction
        if before != -1:
            query += ' AND'
            query += " created < %s" % str(before)
        #After restriction
        if after != -1:
            if before != -1:
                query += ' AND'
            query += " created > %s" % str(after)

        #Order of results
        query += ' ORDER BY created DESC'

        #Limit the number of resulst return
        if number_of_messages > -1:
            query += ' LIMIT ' + str(number_of_messages)

        #Execute main SQL Statement
        cur.execute(query)
        #Get results
        rows = cur.fetchall()
        if rows is None:
            return None
        #Build the return object
        messages = []
        for row in rows:
            message = self._create_message_object(row)
            messages.append(message)
        return messages


    def delete_message(self, message_id):
        '''
        Delete the message with id given as parameter.

        :param str message:id: id of the message to remove.
        :type message_id: int
        :return: True if the message has been deleted, False otherwise
        :raise: ValueError if message_id not correct format

        '''
        # Check that id correct format
        try:
            message_id = int(message_id)
        except:
            raise ValueError


        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # Check if message exists
        cur.execute('SELECT * from messages WHERE message_id = %s' % message_id)
        row = cur.fetchone()
        if row is None:
            return False

        cur.execute('DELETE FROM messages WHERE message_id = %s' % message_id)

        if cur.rowcount < 1:
            return False
        else:
            self.con.commit()
            return True


    def create_message(self, room_id, user_id, content):
        '''
        Create a new message with the data provided as arguments.

        :param int room_id: the room where the message was sent to
        :param str content: the message's content
        :param str user_id: the user_id of the person who is editing this
            message.

        :return: the id of the created message or None if the message was
            not found. Note that it is a string with the format msg-\d{1,3}.

        :raises ChirrupDatabaseError: if the database could not be modified.
        :raises ValueError: if parameters in wrong format

        '''
        try:
            room_id = int(room_id)
            user_id = int(user_id)
        except:
            raise ValueError

        if not isinstance(content, basestring):
            raise ValueError

        self.set_foreign_keys_support()

        # row initialization
        self.con.row_factory = sqlite3.Row

        cur = self.con.cursor()

        # make a query to messages table
        params = (room_id, user_id, content, int(time.mktime(datetime.now().timetuple())))
        stmnt = 'INSERT INTO messages (room_id, user_id, content, created) VALUES (?,?,?,?)'

        cur.execute(stmnt, params)
        message_id = cur.lastrowid
        self.con.commit()

        return message_id

    #MESSAGE UTILS

    def contains_message(self, message_id):
        '''
        Checks if a message is in the database.

        :param str messageid: Id of the message to search. Note that messageid
            is a string with the format msg-\d{1,3}.
        :return: True if the message is in the database. False otherwise.

        '''
        try:
            message_id = int(message_id)
        except:
            raise ValueError
        return self.get_message(message_id) is not None


    #ACCESSING THE USER and USER_PROFILE tables
    def get_users(self):
        '''
        Extracts all users in the database.

        :return: list of Users-object of the database.  None is returned if the database has no users.
        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the users
        query = 'SELECT user.*, user_profile.* FROM user, user_profile \
                 WHERE user.user_id = user_profile.user_id'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the cursor
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        cur.execute(query)
        #Process the results
        rows = cur.fetchall()
        if rows is None:
            return None
        #Process the response.
        users = []
        for row in rows:
            users.append(self._create_user_object(row))
        return users

    def get_user(self, user_id):
        '''
        Extracts all the information of a user.

        :param int user_id:
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_user_object` or None if the user doesn't exist
        :raise ValueError if user_id not valid

        '''

        # check if user_id valid
        try:
            user_id = int(user_id)
        except:
            raise ValueError

        # Init
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # Check if user exists
        cur.execute('SELECT * from user WHERE user_id = %s' % user_id)
        row = cur.fetchone()
        if row is None:
            return None

        query = 'SELECT user.*, user_profile.* FROM users, user_profile \
                          WHERE user.user_id = ? \
                          AND user_profile.user_id = user.user_id'
        # Create first the value
        pvalue = (user_id, )
        cur.execute(query, pvalue)
        #Process the response. Only one posible row is expected.
        row = cur.fetchone()
        return self._create_user_object(row)

    def delete_user(self, user_id):
        '''
        Set ``status`` of the user to "INACTIVE". The information can be retrieved if the user wants it.

        :param int user_id: The user_id of the user to .

        :return: True if the user is deleted, False otherwise.
        :raise: ValueError if user_id not valid

        '''

        #TODO: if user admin in a room return False.

        # check if user_id valid
        try:
            user_id = int(user_id)
        except:
            raise ValueError

        # Init
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        cur.execute('UPDATE user SET status = "INACTIVE" WHERE user_id = %s' % user_id)
        self.con.commit()

        #Check that it has been deleted
        if cur.rowcount < 1:
            return False
        return True

    def modify_user(self, user_id, user):
        '''
        Modify the information of a user.

        :param int user_id: The nickname of the user to modify
        :param user: a dictionary with the following format:

            .. code-block:: javascript

                {'public_profile':{'nickname':,'image':''},
                'restricted_profile':{'username':'','password':'','email':'',
                                      'status':'','created':'','updated':''}
                }

            where:

            * ``nickname``: nickname of the user
            * ``image``: name of the image file

            * ``username``: used for login
            * ``password``: used for login
            * ``email``: current email of the user, login and user contact purposes
            * ``status``: ACTIVE/INACTIVE, deleting a user sets this field INACTIVE.
            * ``created``: when the user account was created, UNIX timestamp when the user registered in the system (long integer)
            * ``updated``: when the user account was modified, UNIX timestamp when the user registered in the system (long integer)

            Note that all values are string if they are not otherwise indicated.


        :return: the user_id of the modified user or None if the
            ``user_id`` passed as parameter is not in the database.
        :raise ValueError: if the user argument is not well formed.

        '''
        # check if user_id valid
        try:
            user_id = int(user_id)
        except:
            raise ValueError

        # Init
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # Check if user exists
        cur.execute('SELECT * from user WHERE user_id = %s' % user_id)
        row = cur.fetchone()
        if row is None:
            return None

        query = 'UPDATE user_profile SET nickname = ?, image = ? WHERE user_id = ?'
        '''
        #temporal variables
        p_profile = user['public_profile']
        r_profile = user['restricted_profile']
        _firstname = r_profile.get('firstname', None)
        _lastname = r_profile.get('lastname', None)
        _email = r_profile.get('email', None)
        _website = r_profile.get('website', None)
        _picture = r_profile.get('picture', None)
        _mobile = r_profile.get('mobile', None)
        _skype = r_profile.get('skype', None)
        _age = r_profile.get('age', None)
        _residence = r_profile.get('residence', None)
        _gender = r_profile.get('gender', None)
        _signature = p_profile.get('signature', None)
        _avatar = p_profile.get('avatar', None)

        #Execute the statement to extract the id associated to a nickname
        pvalue = (nickname,)
        cur.execute(query1, pvalue)
        #Only one value expected
        row = cur.fetchone()
        #if does not exist, return
        if row is None:
            return None
        else:
            user_id = row["user_id"]
            #execute the main statement
            pvalue = (_firstname, _lastname, _email, _website, _picture,
                      _mobile, _skype, _age, _residence, _gender,
                      _signature, _avatar, user_id)
            cur.execute(query2, pvalue)
            self.con.commit()
            #Check that I have modified the user
            if cur.rowcount < 1:
                return None
            return nickname
    '''

    def append_user(self, nickname, user):
        '''
        Create a new user in the database.

        :param str nickname: The nickname of the user to modify
        :param dict user: a dictionary with the information to be modified. The
                dictionary has the following structure:

                .. code-block:: javascript

                    {'public_profile':{'registrationdate':,'signature':'',
                                       'avatar':''},
                    'restricted_profile':{'firstname':'','lastname':'',
                                          'email':'', 'website':'','mobile':'',
                                          'skype':'','age':'','residence':'',
                                          'gender':'', 'picture':''}
                    }

                where:

                * ``registrationdate``: UNIX timestamp when the user registered
                    in the system (long integer)
                * ``signature``: text chosen by the user for signature
                * ``avatar``: name of the image file used as avatar
                * ``firstanme``: given name of the user
                * ``lastname``: family name of the user
                * ``email``: current email of the user.
                * ``website``: url with the user's personal page. Can be None
                * ``mobile``: string showing the user's phone number. Can be
                    None.
                * ``skype``: user's nickname in skype. Can be None.
                * ``residence``: complete user's home address.
                * ``picture``: file which contains an image of the user.
                * ``gender``: User's gender ('male' or 'female').
                * ``age``: integer containing the age of the user.

            Note that all values are string if they are not otherwise indicated.

        :return: the nickname of the modified user or None if the
            ``nickname`` passed as parameter is not  in the database.
        :raise ValueError: if the user argument is not well formed.

        '''
        #Create the SQL Statements
          #SQL Statement for extracting the userid given a nickname
        query1 = 'SELECT user_id from users WHERE nickname = ?'
          #SQL Statement to create the row in  users table
        query2 = 'INSERT INTO users(nickname,regDate,lastLogin,timesviewed)\
                  VALUES(?,?,?,?)'
          #SQL Statement to create the row in user_profile table
        query3 = 'INSERT INTO users_profile (user_id, firstname,lastname, \
                                             email,website, \
                                             picture,mobile, \
                                             skype,age,residence, \
                                             gender,signature,avatar)\
                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'
        #temporal variables for user table
        #timestamp will be used for lastlogin and regDate.
        timestamp = time.mktime(datetime.now().timetuple())
        timesviewed = 0
        #temporal variables for user profiles
        p_profile = user['public_profile']
        r_profile = user['restricted_profile']
        _firstname = r_profile.get('firstname', None)
        _lastname = r_profile.get('lastname', None)
        _email = r_profile.get('email', None)
        _website = r_profile.get('website', None)
        _picture = r_profile.get('picture', None)
        _mobile = r_profile.get('mobile', None)
        _skype = r_profile.get('skype', None)
        _age = r_profile.get('age', None)
        _residence = r_profile.get('residence', None)
        _gender = r_profile.get('gender', None)
        _signature = p_profile.get('signature', None)
        _avatar = p_profile.get('avatar', None)
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to extract the id associated to a nickname
        pvalue = (nickname,)
        cur.execute(query1, pvalue)
        #No value expected (no other user with that nickname expected)
        row = cur.fetchone()
        #If there is no user add rows in user and user profile
        if row is None:
            #Add the row in users table
            # Execute the statement
            pvalue = (nickname, timestamp, timestamp, timesviewed)
            cur.execute(query2, pvalue)
            #Extrat the rowid => user-id
            lid = cur.lastrowid
            #Add the row in users_profile table
            # Execute the statement
            pvalue = (lid, _firstname, _lastname, _email, _website,
                      _picture, _mobile, _skype, _age, _residence, _gender,
                      _signature, _avatar)
            cur.execute(query3, pvalue)
            self.con.commit()
            #We do not do any comprobation and return the nickname
            return nickname
        else:
            return None

    # Room related functionality
    def create_room(self, room_id):
        '''
        Creates a room to the database.
        :param str nickname: nickname of the target user
        :return: a list of users nicknames or None if ``nickname`` is not in the
            database
        '''

    def delete_room(self, room_id):
        '''
        Creates a room to the database.
        :param str nickname: nickname of the target user
        :return: a list of users nicknames or None if ``nickname`` is not in the
            database
        '''

    def modify_room(self, room_id):
        '''
        Creates a room to the database.
        :param str nickname: nickname of the target user
        :return: a list of users nicknames or None if ``nickname`` is not in the
            database
        '''

    def add_room_member(self, room_id, user_id):
        '''
        Creates a room to the database.
        :param str nickname: nickname of the target user
        :return: a list of users nicknames or None if ``nickname`` is not in the
            database
        '''

    def remove_room_member(self, room_id, user_id):
        '''
        Creates a room to the database.
        :param str nickname: nickname of the target user
        :return: a list of users nicknames or None if ``nickname`` is not in the database
        '''

    def get_user_rooms(self, user_id):
        '''
        Gets all the rooms the user has currently joined.

        :param int user_id: user_id of the target user
        :return: a list of rooms or None if ``nickname`` is not in the database

        '''

    def get_rooms(self, keyword='', room_status='', number_of_rooms=-1, before=-1, after=-1):
        # TODO find a good set of parameters for filtering the rooms
        '''
        Return a list of all the rooms in the database filtered by the
        conditions provided in the parameters.

        :param number_of_rooms: default -1. Sets the maximum number of
            messages returning in the list. If set to -1, there is no limit.
        :type number_of_rooms: int
        :param before: All timestamps > ``before`` (UNIX timestamp) are removed.
            If set to -1, this condition is not applied.
        :type before: long
        :param after: All timestamps < ``after`` (UNIX timestamp) are removed.
            If set to -1, this condition is not applied.
        :type after: long

        :return: A list of messages. Each message is a dictionary containing
            the following keys:

            * ``message_id``: int
            * ``room_id``: room_id where the message was sent to.
            * ``user_id``: user_id of the message's author.
            * ``content``: string containing the title of the message.
            * ``created``: UNIX timestamp (long int) that specifies when the
                message was created.

            Note that all values in the returned dictionary are string unless
            otherwise stated.

            None is returned if the room_id doesn't exist.

        :raises ValueError: if ``before`` or ``after`` are not valid UNIX
            timestamps or ``before`` > ``after`` or arguments type is not int.

        '''
        # Check input parameters
        if type(number_of_rooms) is not int or type(before) is not int or type(after) is not int:
            raise ValueError

        if after > before:
            raise ValueError

        # Initialization
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # Create the SQL Statement build the string depending on the existence
        # of room_id, numbero_of_messages, before and after arguments.
        query = 'SELECT * FROM messages WHERE '

        # Before restriction
        if before != -1:
            query += ' AND'
            query += " created < %s" % str(before)
        # After restriction
        if after != -1:
            if before != -1:
                query += ' AND'
            query += " created > %s" % str(after)

        # Order of results
        query += ' ORDER BY created DESC'

        # Limit the number of resulst return
        if number_of_rooms > -1:
            query += ' LIMIT ' + str(number_of_rooms)

        # Execute main SQL Statement
        cur.execute(query)
        # Get results
        rows = cur.fetchall()
        if rows is None:
            return None
        # Build the return object
        messages = []
        for row in rows:
            message = self._create_message_object(row)
            messages.append(message)
        return messages

    # UTILS
    # do we need or is it gonna be username or maybe email?
    def get_user_id(self, nickname):
        '''
        Get the key of the database row which contains the user with the given
        nickname.

        :param str nickname: The nickname of the user to search.
        :return: the database attribute user_id  or None if ``nickname`` does not exit.
        :rtype: int

        '''
        # Init
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        query = 'SELECT * FROM users WHERE nickname = ?'

        pvalue = (nickname,)
        cur.execute(query, pvalue)

        row = cur.fetchone()
        if row is None:
            return None

        return int(row['user_id'])


    def get_room_id(self, name):
        '''
        Get the key of the database row which contains the user with the given
        name of the room.

        :param str name: The name of the room to search.
        :return: the database attribute room_id(INTEGER) or None if ``name`` does not exit.
        :raise: ValueError if name not string
        :rtype: int

        '''

        if not isinstance(name, basestring):
            raise ValueError

        # Init
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        cur.execute('SELECT room_id FROM room WHERE name = %s' % name)

        # return None if room doesn't exist
        row = cur.fetchone()
        if row is None:
            return None

        return int(row['room_id'])


