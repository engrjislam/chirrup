# course exercise1 database.py used as a template

from datetime import datetime
import time, sqlite3, re
#Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/chirrup.db'
DEFAULT_SCHEMA = "db/chirrup_schema_dump.sql"
DEFAULT_DATA_DUMP = "db/chirrup_data_dump.sql"


class Connection(object):
    '''
    API to access the Forum database.

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

            * ``messageid``: id of the message (int)
            * ``title``: message's title
            * ``body``: message's text
            * ``timestamp``: UNIX timestamp (long integer) that specifies when
              the message was created.
            * ``replyto``: The id of the parent message. String with the format
              msg-{id}. Its value can be None.
            * ``sender``: The nickname of the message's creator.
            * ``editor``: The nickname of the message's editor.

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        '''
        message_id = 'msg-' + str(row['message_id'])
        message_replyto = 'msg-' + str(row['reply_to']) \
            if row['reply_to'] is not None else None
        message_sender = row['user_nickname']
        message_editor = row['editor_nickname']
        message_title = row['title']
        message_body = row['body']
        message_timestamp = row['timestamp']
        message = {'messageid': message_id, 'title': message_title,
                   'timestamp': message_timestamp, 'replyto': message_replyto,
                   'body': message_body, 'sender': message_sender,
                   'editor': message_editor}
        return message

    def _create_message_list_object(self, row):
        '''
        Same as :py:meth:`_create_message_object`. However, the resulting
        dictionary is targeted to build messages in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``messageid``, ``title``,
            ``timestamp`` and ``sender``.

        '''
        message_id = 'msg-' + str(row['message_id'])
        message_sender = row['user_nickname']
        message_title = row['title']
        message_timestamp = row['timestamp']
        message = {'messageid': message_id, 'title': message_title,
                   'timestamp': message_timestamp, 'sender': message_sender}
        return message

    #Helpers for users
    def _create_user_object(self, row):
        '''
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following format:

            .. code-block:: javascript

                {'public_profile':{'registrationdate':,'nickname':'',
                                   'signature':'','avatar':''},
                'restricted_profile':{'firstname':'','lastname':'','email':'',
                                      'website':'','mobile':'','skype':'',
                                      'age':'','residence':'','gender':'',
                                      'picture':''}
                }

            where:

            * ``registrationdate``: UNIX timestamp when the user registered in
                                 the system (long integer)
            * ``nickname``: nickname of the user
            * ``signature``: text chosen by the user for signature
            * ``avatar``: name of the image file used as avatar
            * ``firstanme``: given name of the user
            * ``lastname``: family name of the user
            * ``email``: current email of the user.
            * ``website``: url with the user's personal page. Can be None
            * ``mobile``: string showing the user's phone number. Can be None.
            * ``skype``: user's nickname in skype. Can be None.
            * ``residence``: complete user's home address.
            * ``picture``: file which contains an image of the user.
            * ``gender``: User's gender ('male' or 'female').
            * ``age``: integer containing the age of the user.

            Note that all values are string if they are not otherwise indicated.

        '''
        reg_date = row['regDate']
        return {'public_profile': {'registrationdate': reg_date,
                                   'nickname': row['nickname'],
                                   'signature': row['signature'],
                                   'avatar': row['avatar']},
                'restricted_profile': {'firstname': row['firstname'],
                                       'lastname': row['lastname'],
                                       'email': row['email'],
                                       'website': row['website'],
                                       'mobile': row['mobile'],
                                       'skype': row['skype'],
                                       'age': row['age'],
                                       'residence': row['residence'],
                                       'gender': row['gender'],
                                       'picture': row['picture']}
                }

    def _create_user_list_object(self, row):
        '''
        Same as :py:meth:`_create_message_object`. However, the resulting
        dictionary is targeted to build messages in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``registrationdate`` and
            ``nickname``

        '''
        return {'registrationdate': row['regDate'], 'nickname': row['nickname']}

    #API ITSELF
    #Message Table API.
    def get_message(self, messageid):
        '''
        Extracts a message from the database.

        :param messageid: The id of the message. Note that messageid is a
            string with format ``msg-\d{1,3}``.
        :return: A dictionary with the format provided in
            :py:meth:`_create_message_object` or None if the message with target
            id does not exist.
        :raises ValueError: when ``messageid`` is not well formed

        '''
        #Extracts the int which is the id for a message in the database
        match = re.match(r'msg-(\d{1,3})', messageid)
        if match is None:
            raise ValueError("The messageid is malformed")
        messageid = int(match.group(1))
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the SQL Query
        query = 'SELECT * FROM messages WHERE message_id = ?'
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = (messageid,)
        cur.execute(query, pvalue)
        #Process the response.
        #Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        #Build the return object
        return self._create_message_object(row)

    def get_messages(self, nickname=None, number_of_messages=-1,
                     before=-1, after=-1):
        '''
        Return a list of all the messages in the database filtered by the
        conditions provided in the parameters.

        :param nickname: default None. Search messages of a user with the given
            nickname. If this parameter is None, it returns the messages of
            any user in the system.
        :type nickname: str
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

            * ``messageid``: string with the format msg-\d{1,3}.Id of the
                message.
            * ``sender``: nickname of the message's author.
            * ``title``: string containing the title of the message.
            * ``timestamp``: UNIX timestamp (long int) that specifies when the
                message was created.

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        :raises ValueError: if ``before`` or ``after`` are not valid UNIX
            timestamps

        '''
        #Create the SQL Statement build the string depending on the existence
        #of nickname, numbero_of_messages, before and after arguments.
        query = 'SELECT * FROM messages'
          #Nickname restriction
        if nickname is not None or before != -1 or after != -1:
            query += ' WHERE'
        if nickname is not None:
            query += " user_nickname = '%s'" % nickname
          #Before restriction
        if before != -1:
            if nickname is not None:
                query += ' AND'
            query += " timestamp < %s" % str(before)
          #After restriction
        if after != -1:
            if nickname is not None or before != -1:
                query += ' AND'
            query += " timestamp > %s" % str(after)
          #Order of results
        query += ' ORDER BY timestamp DESC'
          #Limit the number of resulst return
        if number_of_messages > -1:
            query += ' LIMIT ' + str(number_of_messages)
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        cur.execute(query)
        #Get results
        rows = cur.fetchall()
        if rows is None:
            return None
        #Build the return object
        messages = []
        for row in rows:
            message = self._create_message_list_object(row)
            messages.append(message)
        return messages

    def delete_message(self, messageid):
        '''
        Delete the message with id given as parameter.

        :param str messageid: id of the message to remove.Note that messageid
            is a string with format ``msg-\d{1,3}``
        :return: True if the message has been deleted, False otherwise
        :raises ValueError: if the messageId has a wrong format.

        '''
        #Extracts the int which is the id for a message in the database
        match = re.match(r'msg-(\d{1,3})', messageid)
        if match is None:
            raise ValueError("The messageid is malformed")
        messageid = int(match.group(1))
        '''
        #TASK5 TODO:#
        * Implement this method.
        * HINTS:
           * To remove a message use the DELETE sql command
           * To check if the message has been previously deleted you can check
             the size of the rows returned in the cursor. You can check it from
             the attribute cursor.rowcount. If the rowcount is < 1 means that
             no row has been  deleted and hence you should return False.
             Otherwise return True.
           * Be sure that you commit the current transaction
        * HOW TO TEST: Use the database_api_tests_message. The following tests
          must pass without failure or error:
            * test_delete_message
            * test_delete_message_malformed_id
            * test_delete_message_noexisting_id
        '''

        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # Check if message exists
        cur.execute('SELECT * from messages WHERE message_id = %s' % messageid)
        row = cur.fetchone()
        if row is None:
            return False

        cur.execute('DELETE FROM messages WHERE message_id = %s' % messageid)

        if cur.rowcount < 1:
            return False
        else:
            self.con.commit()
            return True

    def create_room(room):
        '''
        Creates a room to the database.

        :param str nickname: nickname of the target user
        :return: a list of users nicknames or None if ``nickname`` is not in the
            database
        '''


    def create_message(self, title, body, sender="Anonymous",
                       ipaddress="0.0.0.0", replyto=None):
        '''
        Create a new message with the data provided as arguments.

        :param str title: the message's title
        :param str body: the message's content
        :param str sender: the nickname of the person who is editing this
            message. If it is not provided "Anonymous" will be stored in db.
        :param str ipaddress: The ip address from which the message was created.
            It is a string with format "xxx.xxx.xxx.xxx". If no ipaddress is
            provided then database will store "0.0.0.0"
        :param str replyto: Only provided if this message is an answer to a
            previous message (parent). Otherwise, Null will be stored in the
            database. The id of the message has the format msg-\d{1,3}

        :return: the id of the created message or None if the message was
            not found. Note that it is a string with the format msg-\d{1,3}.

        :raises ForumDatabaseError: if the database could not be modified.
        :raises ValueError: if the replyto has a wrong format.

        '''
        #Extracts the int which is the id for a message in the database
        if replyto is not None:
            match = re.match('msg-(\d{1,3})', replyto)
            if match is None:
                raise ValueError("The replyto is malformed")
            replyto = int(match.group(1))

        self.set_foreign_keys_support()

        # row initialization
        self.con.row_factory = sqlite3.Row

        cur = self.con.cursor()

        # fetch user_id if the sender nickname not "Anomynous"
        if sender == "Anonymous":
            user_id = None
        else:
            cur.execute('SELECT user_id from users WHERE nickname = "%s"' % sender)

            row = cur.fetchone()
            if row is None:
               user_id = None
            else:
                user_id = row["user_id"]

        # Check if message exists
        if replyto is not None:
            cur.execute('SELECT * from messages WHERE message_id = %s' % replyto)
            row = cur.fetchone()
            if row is None:
                return None

        # make a query to messages table to get the last id
        params = (title, body, time.mktime(datetime.now().timetuple()), ipaddress, 0, replyto, sender, user_id)
        stmnt = 'INSERT INTO messages (title, body, timestamp, ip, timesviewed, reply_to, user_nickname, user_id) \
                VALUES (?,?,?,?,?,?,?,?)'

        cur.execute(stmnt, params)
        message_id = cur.lastrowid
        self.con.commit()

        return 'msg-' + str(message_id)

    #MESSAGE UTILS

    def contains_message(self, messageid):
        '''
        Checks if a message is in the database.

        :param str messageid: Id of the message to search. Note that messageid
            is a string with the format msg-\d{1,3}.
        :return: True if the message is in the database. False otherwise.

        '''
        return self.get_message(messageid) is not None


    #ACCESSING THE USER and USER_PROFILE tables
    def get_users(self):
        '''
        Extracts all users in the database.

        :return: list of Users of the database. Each user is a dictionary
            that contains two keys: ``nickname``(str) and ``registrationdate``
            (long representing UNIX timestamp). None is returned if the database
            has no users.

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the users
        query = 'SELECT users.*, users_profile.* FROM users, users_profile \
                 WHERE users.user_id = users_profile.user_id'
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
            users.append(self._create_user_list_object(row))
        return users

    def get_user(self, nickname):
        '''
        Extracts all the information of a user.

        :param str nickname: The nickname of the user to search for.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_user_object`

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the user given a nickname
        query1 = 'SELECT user_id from users WHERE nickname = ?'
          #SQL Statement for retrieving the user information
        query2 = 'SELECT users.*, users_profile.* FROM users, users_profile \
                  WHERE users.user_id = ? \
                  AND users_profile.user_id = users.user_id'
          #Variable to be used in the second query.
        user_id = None
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute SQL Statement to retrieve the id given a nickname
        pvalue = (nickname,)
        cur.execute(query1, pvalue)
        #Extract the user id
        row = cur.fetchone()
        if row is None:
            return None
        user_id = row["user_id"]
        # Execute the SQL Statement to retrieve the user invformation.
        # Create first the valuse
        pvalue = (user_id, )
        #execute the statement
        cur.execute(query2, pvalue)
        #Process the response. Only one posible row is expected.
        row = cur.fetchone()
        return self._create_user_object(row)

    def delete_user(self, nickname):
        '''
        Remove all user information of the user with the nickname passed in as
        argument.

        :param str nickname: The nickname of the user to remove.

        :return: True if the user is deleted, False otherwise.

        '''
        #Create the SQL Statements
          #SQL Statement for deleting the user information
        query = 'DELETE FROM users WHERE nickname = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (nickname,)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that it has been deleted
        if cur.rowcount < 1:
            return False
        return True

    def modify_user(self, nickname, user):
        '''
        Modify the information of a user.

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
        #SQL Statement to update the user_profile table
        query2 = 'UPDATE users_profile SET firstname = ?,lastname = ?, \
                                           email = ?,website = ?, \
                                           picture = ?,mobile = ?, \
                                           skype = ?,age = ?,residence = ?, \
                                           gender = ?,signature = ?,avatar = ?\
                                           WHERE user_id = ?'
        #temporal variables
        user_id = None
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

    # UTILS

    # don't have
    def get_user_id(self, nickname):
        '''
        Get the key of the database row which contains the user with the given
        nickname.

        :param str nickname: The nickname of the user to search.
        :return: the database attribute user_id or None if ``nickname`` does
            not exit.
        :rtype: str

        '''

        '''
        TASK5 TODO :
        * Implement this method.
        HINTS:
          * Check the method get_message as an example.
          * The value to return is a string and not a dictionary
          * You can access the columns of a database row in the same way as
            in a python dictionary: row [attribute] (Check the exercises slides
            for more information)
          * There is only one possible user_id associated to a nickname
          * HOW TO TEST: Use the database_api_tests_user. The following tests
            must pass without failure or error:
                * test_get_user_id
                * test_get_user_id_unknown_user
        '''

        self.set_foreign_keys_support()

        query = 'SELECT * FROM users WHERE nickname = ?'

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        pvalue = (nickname,)
        cur.execute(query, pvalue)

        row = cur.fetchone()
        if row is None:
            return None

        return row['user_id']

    def contains_user(self, nickname):
        '''
        :return: True if the user is in the database. False otherwise
        '''
        return self.get_user_id(nickname) is not None
