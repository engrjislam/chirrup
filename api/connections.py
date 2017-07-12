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

    # FOREIGN KEY STATUS
    def check_foreign_keys_status(self):
        '''
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.

        '''
        try:
            # Create a cursor to receive the database values
            cur = self.con.cursor()
            # Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            # We know we retrieve just one record: use fetchone()
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
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            # execute the pragma command, ON
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
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            # execute the pragma command, OFF
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    # HELPERS
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

    # Helpers for users
    def _create_user_object(self, row):
        '''
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following format:

            .. code-block:: javascript

                {'public_profile':{'nickname':,'image':''},
                'restricted_profile':{'username':'','email':'',
                                      'status':'','created':'','updated':''}
                }

            where:

            * ``nickname``: nickname of the user
            * ``image``: name of the image file

            * ``username``: used for login
            * ``email``: current email of the user, login and user contact purposes
            * ``status``: ACTIVE/INACTIVE, deleting a user sets this field INACTIVE.
            * ``created``: when the user account was created, UNIX timestamp when the user registered in the system (long integer)
            * ``updated``: when the user account was modified, UNIX timestamp when the user registered in the system (long integer)

            Note that all values are string if they are not otherwise indicated.

        '''
        return {'public_profile': {'nickname': str(row['nickname']),
                                   'image': str(row['image'])},
                'restricted_profile': {'user_id': str(row['user_id']),
                                       'username': str(row['username']),
                                       'email': str(row['email']),
                                       'status': str(row['status']),
                                       'created': str(row['created']),
                                       'updated': str(row['updated'])}
                }

    # for public information, needed??
    def _create_user_public_object(self, row):
        '''
        Same as :py:meth:`_create_message_object`. However, the resulting
        dictionary is targeted to build messages in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``registrationdate`` and
            ``nickname``
        '''

        return {'registrationdate': row['regDate'], 'nickname': row['nickname']}

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

    def _check_if_exists(self, cursor, id, id_type, table):
        # FUNCTION NOT USED YET
        '''
        Checks if e.g. user exists in a user-table. Id checks already done in the upper level.
        :param connection.cursor(): current cursor object
        :param int id: identifier
        :param string table: name of the table
        :return: True if id exists, False otherwise
        '''

        cursor.execute('SELECT * from %s WHERE %s = %s' % (table, id_type, id))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def _check_id(self, id):
        '''
        Checks if id possible to convert to int.
        :param id:
        :return: id
        :raise: ValueError if conversion not possible
        '''
        try:
            id = int(id)
        except:
            raise ValueError

        return id

    # API ITSELF
    # Message Table API.
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

        message_id = self._check_id(message_id)

        # Init
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        query = 'SELECT * FROM messages WHERE message_id = ?'

        # Execute the query
        pvalue = (message_id,)
        cur.execute(query, pvalue)
        # Process the response.
        # Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        # Build the return object
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
        if number_of_messages > -1:
            query += ' LIMIT ' + str(number_of_messages)

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
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # make a query to messages table
        params = (room_id, user_id, content, int(time.mktime(datetime.now().timetuple())))
        stmnt = 'INSERT INTO messages (room_id, user_id, content, created) VALUES (?,?,?,?)'

        cur.execute(stmnt, params)
        message_id = cur.lastrowid
        self.con.commit()

        return message_id

    # MESSAGE UTILS

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

    # ACCESSING THE USER and USER_PROFILE tables
    def get_users(self):
        '''
        Extracts all users in the database.

        :return: list of Users-object of the database.  None is returned if the database has no users.
        '''
        # Create the SQL Statements
        # SQL Statement for retrieving the users
        query = 'SELECT user.*, user_profile.* FROM user, user_profile \
                 WHERE user.user_id = user_profile.user_id'
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Create the cursor
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement
        cur.execute(query)
        # Process the results
        rows = cur.fetchall()
        if rows is None:
            return None
        # Process the response.
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
        pvalue = (user_id,)
        cur.execute(query, pvalue)
        # Process the response. Only one possible row is expected.
        row = cur.fetchone()
        return self._create_user_object(row)

    def delete_user(self, user_id):
        '''
        Set ``status`` of the user to "INACTIVE". The information can be retrieved if the user wants it.
        If the user is an admin in a room, the user cannot be removed.

        :param int user_id: The user_id of the user to .
        :return: True if the user is deleted, False otherwise.
        :raise: ValueError if user_id not valid
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

        # check if user admin in a room
        cur.execute('SELECT * from room WHERE admin = %s' % user_id)
        row = cur.fetchone()
        if row is not None:
            return False

        cur.execute('UPDATE user SET status = "INACTIVE" WHERE user_id = %s' % user_id)
        self.con.commit()

        # Check that it has been deleted
        if cur.rowcount < 1:
            # maybe return the list of rooms where admin?
            return False
        return True

    def modify_user(self, user_id, user):
        '''
        Modify the information of a user.

        :param int user_id: The nickname of the user to modify
        :param user: a dictionary with the following format:

            .. code-block:: javascript

                {'public_profile':{'nickname':,'image':''},
                'restricted_profile':{'username':'','email':'',
                                      'status':'','created':'','updated':''}
                }

            where:

            * ``nickname``: nickname of the user
            * ``image``: name of the image file

            * ``username``: used for login
            * ``email``: current email of the user, login and user contact purposes
            * ``status``: ACTIVE/INACTIVE, deleting a user sets this field INACTIVE.
            * ``created``: when the user account was created, UNIX timestamp when the user registered in the system (long integer)
            * ``updated``: when the user account was modified, UNIX timestamp when the user registered in the system (long integer)

            Note that all values are string if they are not otherwise indicated.

        :return: the user_id of the modified user or None if the
            ``user_id`` passed as parameter is not in the database.
        :raise ValueError: if the user argument is not well formed.
        :raise sqlite3.DatabaseError: if database action not allowed

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

        nickname = user['public_profile']['nickname']
        image = user['public_profile']['image']
        username = user['private_profile']['username']
        email = user['private_profile']['email']

        # query for updating user profile
        params1 = (nickname, image, user_id)
        query1 = 'UPDATE user_profile SET nickname = ?, image = ? WHERE user_id = ?'

        # query for updating info in the user-table
        params2 = (username, email, int(time.mktime(datetime.now().timetuple())), user_id)
        query2 = 'UPDATE user SET username = ?, email = ?, updated = ? WHERE user_id = ?'

        try:
            cur.execute(query1, params1)
        except sqlite3.DatabaseError:
            raise

        self.con.commit()
        # Check that the room has been modified
        if cur.rowcount < 1:
            return None

        try:
            cur.execute(query2, params2)
        except sqlite3.DatabaseError:
            raise

        self.con.commit()
        # Check that the room has been modified
        if cur.rowcount < 1:
            return None

        return user_id

    def append_user(self, user):
        # TODO is user status needed in the user object? Should there exist a different kind of user object?
        '''
        Append a new user.

        :param user: a dictionary with the following format:

            .. code-block:: javascript

                {'public_profile':{'nickname':,'image':''},
                'restricted_profile':{'username':'','email':'',
                                      'status':'','created':'','updated':''}
                }

            where:

            * ``nickname``: nickname of the user
            * ``image``: name of the image file

            * ``username``: used for login
            * ``email``: current email of the user, login and user contact purposes
            * ``status``: ACTIVE/INACTIVE, deleting a user sets this field INACTIVE.
            * ``created``: when the user account was created, UNIX timestamp when the user registered in the system (long integer)
            * ``updated``: when the user account was modified, UNIX timestamp when the user registered in the system (long integer)

            Note that all values are string if they are not otherwise indicated.

        :return: the user_id of the modified user or False if creation failed.
        :raise ValueError: if the user argument is not well formed.
        :raise sqlite3.DatabaseError: if database action not allowed

        '''

        # Init
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        nickname = user['public_profile']['nickname']
        image = user['public_profile']['image']
        username = user['private_profile']['username']
        email = user['private_profile']['email']

        # query for updating info in the user-table
        params1 = (username, email, 'ACTIVE', int(time.mktime(datetime.now().timetuple())))
        query1 = 'INSERT INTO user (username, email, status, created) \
                  VALUES(?, ?, ?, ?)'
        try:
            cur.execute(query1, params1)
        except sqlite3.DatabaseError:
            raise

        self.con.commit()
        # Check that the user has been created
        if cur.rowcount < 1:
            return None
        else:
            if cur.lastrowid is None:
                return False
            user_id = int(cur.lastrowid)

            # query for updating user profile
            params2 = (nickname, image, user_id)
            query2 = 'UPDATE user_profile SET nickname = ?, image = ? WHERE user_id = ?'

            try:
                cur.execute(query2, params2)
            except sqlite3.DatabaseError:
                raise

            self.con.commit()
            # Check that the room has been modified
            if cur.rowcount < 1:
                return None

            return user_id

    # Room related functionality
    def create_room(self, name, type, admin):
        '''
        Create a new room with the data provided as arguments.
        :param str name: the name of the room
        :param str type: 'PUBLIC'/'PRIVATE'
        :param int admin: user_id of the admin of the room
        DEFAULT SHOULD BE THE USER WHO CREATED THE ROOM
        :return: the id of the created message or False if the room creation failed
        :raises ValueError: if parameters in wrong format
        :raises sqlite3.IntegrityError: if room name already in use
        '''

        # check parameters
        if not isinstance(name, basestring) or not isinstance(type, basestring):
            raise ValueError
        admin = self._check_id(admin)

        if type not in ['PUBLIC', 'PRIVATE']:
            raise ValueError

        # Init
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # check if admin exists
        cur.execute('SELECT * from user WHERE user_id = %s' % admin)
        row = cur.fetchone()
        if row is not None:
            return False

        params = (name, type, admin, int(time.mktime(datetime.now().timetuple())))
        stmnt = 'INSERT INTO room VALUES (NULL, ?, ?, ?, "ACTIVE", ?, NULL)'

        # raises sqlite3.IntegrityError when trying to add a room which name is already in use
        try:
            cur.execute(stmnt, params)
        except sqlite3.IntegrityError:
            raise

        room_id = cur.lastrowid
        self.con.commit()

        return int(room_id)

    def delete_room(self, room_id):
        '''
        Set ``status`` of the room to "INACTIVE". The information can be retrieved if the admin wants it.
        (functionality not yet implemented)
        :param int room_id: room identifier
        :return: True if the room is "deleted", False otherwise.
        :raise: ValueError if room_id not valid
        '''

        # check if room_id valid
        try:
            room_id = int(room_id)
        except:
            raise ValueError

        # Init
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # check if room exists
        cur.execute('SELECT * from room WHERE room_id = %s' % room_id)
        row = cur.fetchone()
        if row is not None:
            return False

        cur.execute('UPDATE room SET status = "INACTIVE" WHERE room_id = %s' % room_id)
        self.con.commit()

        # Check that it has been deleted
        if cur.rowcount < 1:
            # maybe return the list of rooms where admin?
            return False
        return True

    def modify_room(self, room_id, room):
        '''
        Modify the information of a room.

        :param int room_id: room identifier
        :param room: a dictionary with the following format:

            * ``name``: name of the room
            * ``type``: "PRIVATE" or "PUBLIC"
            * ``admin``: user_id of the user with admin privileges, initially given for the user who creates the room
            * ``status``: ACTIVE/INACTIVE, deleting a user sets this field INACTIVE.
            * ``created``: when the room was created, UNIX timestamp (long integer)
            * ``updated``: when the room information(name, type, admin, status) was modified,
             UNIX timestamp (long integer)

            Note that all values are string if they are not otherwise indicated.

        :return: the room_id of the modified user or None if the
            ``room_id`` or room['admin'] is not in the database.
        :raise ValueError: if the user argument is not well formed.

        '''
        self._check_id(room_id)

        # Init
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # Check if room exists
        cur.execute('SELECT * from room WHERE room_id = %s' % room_id)
        row = cur.fetchone()
        if row is None:
            return None

        # check if room parameters valid
        name = room['name']
        if not isinstance(room, basestring):
            raise ValueError

        _type = room['type']
        if _type not in ['PUBLIC', 'PRIVATE']:
            raise ValueError

        admin = int(self._check_id(room['admin']))

        # Check if admin user exists
        cur.execute('SELECT * from user WHERE user_id = %s' % admin)
        row = cur.fetchone()
        if row is None:
            return None

        status = room['STATUS']
        if status not in ['ACTIVE', 'INACTIVE']:
            raise ValueError

        params = (name, _type, admin, status, int(time.mktime(datetime.now().timetuple())), room_id)
        query = 'UPDATE room SET name = ?, type = ?, admin = ?, status = ?, updated = ? WHERE room_id = ?'

        try:
            cur.execute(query, params)
        except sqlite3.IntegrityError:
            raise

        self.con.commit()
        # Check that the room has been modified

        if cur.rowcount < 1:
            return None

        return room_id

    def add_room_member(self, room_id, user_id):
        '''
        Adds a user to a room i.e. adds a row in the room_users table.
        :param int room_id: room identifier
        :param int user_id: user identifier
        :return: True if the member has been added, False if insert-process failed
        or None if room or user don't exist.
        :raise: ValueError if room_id or user_id malformed
        '''

        # check if room_id valid
        try:
            room_id = int(room_id)
            user_id = int(user_id)
        except:
            raise ValueError

        # Initialization
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # Check if user exists
        cur.execute('SELECT * from user WHERE user_id = %s' % user_id)
        row = cur.fetchone()
        if row is None:
            return None

        # Check if room exists
        cur.execute('SELECT * from room WHERE room_id = %s' % room_id)
        row = cur.fetchone()
        if row is None:
            return None

        cur.execute('INSERT INTO room_users (NULL, %s, %s, %s)' % (
        room_id, user_id, int(time.mktime(datetime.now().timetuple()))))

        if cur.rowcount < 1:
            return False
        else:
            self.con.commit()
            return True

    def remove_room_member(self, room_id, user_id):
        '''
        Removes a user from a room i.e. deletes the correct row in the room_users table.
        :param int room_id: room identifier
        :param int use_id: user identifier
        :return: True if the member has been deleted, False if delete-process failed
        or None if room or user don't exist.
        :raise: ValueError if room_id or user_id malformed
        '''

        # check if room_id valid
        try:
            room_id = int(room_id)
            user_id = int(user_id)
        except:
            raise ValueError

        # Initialization
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # Check if user exists
        cur.execute('SELECT * from user WHERE user_id = %s' % user_id)
        row = cur.fetchone()
        if row is None:
            return None

        # Check if room exists
        cur.execute('SELECT * from room WHERE room_id = %s' % room_id)
        row = cur.fetchone()
        if row is None:
            return None

        cur.execute('DELETE FROM room_users WHERE room_id = %s AND user_id = %s' % (room_id, user_id))

        if cur.rowcount < 1:
            return False
        else:
            self.con.commit()
            return True

    def get_room(self, room_id):
        '''
        Gets room information.
        :param int user_id: user_id of the target user
        :return: a room object or None if (``room_id`` is not in the database or the room is set to INACTIVE(deleted))
        :raise: ValueError if room_id malformed
        '''

        # check if room_id valid
        try:
            room_id = int(room_id)
        except:
            raise ValueError

        # Initialization
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        cur.execute('SELECT * FROM room WHERE room_id = %s' % room_id)

        row = cur.fetchall()
        if row is None:
            return None

        # if room 'INACTIVE', don't return it
        if row['status'] == 'INACTIVE':
            return None

        return self._create_room_object(row)

    def get_user_rooms(self, user_id):
        '''
        Gets all the rooms the user has currently joined.

        :param int user_id: user_id of the target user
        :return: list of dictionaries in format:
        {'joined': <UNIX timestamp>, 'room': room_object} or None if ``user_id`` is not in the database
        :raise: ValueError if user_id malformed

        '''
        # check if user_id valid
        try:
            user_id = int(user_id)
        except:
            raise ValueError

        # Initialization
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        cur.execute('SELECT room_id, joined FROM room_users WHERE user_id = %s' % user_id)
        # Get results
        rows = cur.fetchall()
        if rows is None:
            return None

        # append room_ids and timestamps when joined a room to a list,
        room_ids = []
        rooms_joined = []
        rooms = []
        for row in rows:
            room_ids.append(int(row['room_id'], row['joined']))
            rooms_joined.append(int(row['joined']))

        # get room information for every user room, if room doesn't exist or set to 'INACTIVE' pass it
        for index in range(len(room_ids)):
            room = self.get_room(room_ids[index])
            if room != None:
                rooms.append[{'joined': rooms_joined[index], 'room': room}]

        return rooms

    def get_rooms(self, keyword='', room_type='', number_of_rooms=-1, before=-1, after=-1):
        # not tested, additional feature
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
        query = 'SELECT * FROM room WHERE '

        # Before restriction
        if before != -1:
            query += ' AND'
            query += ' created < %s' % str(before)
        # After restriction
        if after != -1:
            if before != -1:
                query += ' AND'
            query += ' created > %s' % str(after)
        # add keyword which filter the room id names
        if keyword:
            if after != -1 or before != -1:
                query += ' AND'
            query += ' name LIKE "%%%s\%%"' % str(keyword)
        # filter with room_status
        if room_type:
            if after != -1 or before != -1 or keyword:
                query += ' AND'
            query += ' type = %s' % str(room_type)

        # Order of results
        query += ' ORDER BY created DESC'

        # Limit the number of rooms returned
        if number_of_rooms > -1:
            query += ' LIMIT ' + str(number_of_rooms)

        # Execute main SQL Statement
        cur.execute(query)
        # Get results
        rows = cur.fetchall()
        if rows is None:
            return None
        # Build the return object
        rooms = []
        for row in rows:
            room = self._create_room_object(row)
            rooms.append(room)

        return rooms

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

    def get_user_nickname(self, user_id):
        '''
        Get the key of the database row which contains the user_profile with the given
        user_id.

        :param int user_id: The unique identificate of the user.
        :return: the database attribute nickname  or None if ``user_id`` does not exit.
        :rtype: str

        '''
        # Init
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        cur.execute('SELECT * FROM user_profile WHERE user_id = %s' % user_id)

        # Return None if the user doesn't exist
        row = cur.fetchone()
        if row is None:
            return None

        return row['nickname']

    def get_room_name(self, room_id):
        '''
        Get the key of the database row which contains the room with the given
        room_id.

        :param int room_id: The unique identificate of the room.
        :return: the database attribute nickname  or None if ``room_id`` does not exit.
        :rtype: str
        :raise: ValueError if room_id malformed

        '''

        # check if room_id valid
        try:
            room_id = int(room_id)
        except:
            raise ValueError

        # Init
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        cur.execute('SELECT * FROM room WHERE room_id = %s' % room_id)

        # Return None if the user doesn't exist
        row = cur.fetchone()
        if row is None:
            return None

        return row['name']

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
