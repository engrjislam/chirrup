'''
Programmable Web Project course exercise 1 database.py used as a template for implementation

Created on 11.07.2017

Provides the database API to access the forum persistent data.

'''

import sqlite3, os, connections

#Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/chirrup.db'
DEFAULT_SCHEMA = "db/chirrup_schema_dump.sql"
DEFAULT_DATA_DUMP = "db/chirrup_data_dump.sql"


class Engine(object):
    '''
    Abstraction of the database.

    It includes tools to create, configure,
    populate and connect to the sqlite file. You can access the Connection
    instance, and hence, to the database interface itself using the method
    :py:meth:`connection`.

    :Example:

    >>> engine = Engine()
    >>> con = engine.connect()

    :param db_path: The path of the database file (always with respect to the
        calling script. If not specified, the Engine will use the file located
        at *db/chirrup.db*

    '''
    def __init__(self, db_path=None):
        '''
        '''

        super(Engine, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH

    def connect(self):
        '''
        Creates a connection to the database.

        :return: A Connection instance
        :rtype: Connection

        '''
        return connections.Connection(self.db_path)

    def remove_database(self):
        '''
        Removes the database file from the filesystem.
        '''
        if os.path.exists(self.db_path):
            #THIS REMOVES THE DATABASE STRUCTURE
            os.remove(self.db_path)

    def remove_tables(self):
        '''
        Removes tables from the database.
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        with con:
            cur = con.cursor()
            # token table
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=token")
            row = cur.fetchone()
            print('row: ', row)
            if row is not None:
                cur.execute("DROP TABLE token")
            # user table
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=user")
            row = cur.fetchone()
            if row is not None:
                cur.execute("DROP TABLE user")
            # user_profile table
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=user_profile")
            row = cur.fetchone()
            if row is not None:
                cur.execute("DROP TABLE user_profile")
            # room table
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=room")
            row = cur.fetchone()
            if row is not None:
                cur.execute("DROP TABLE room")
            # room_users table
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=room_users")
            row = cur.fetchone()
            if row is not None:
                cur.execute("DROP TABLE messages")
            # messages table
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=messages")
            row = cur.fetchone()
            if row is not None:
                cur.execute("DROP TABLE messages")


    def clear(self):
        '''
        Purge the database removing all records from the tables. However,
        it keeps the database schema (meaning the table structure)

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        with con:
            cur = con.cursor()
            #cur.execute("DELETE FROM token")
            cur.execute("DELETE FROM user")

            # ON DELETE CASCADE in user_profile, room, room_users and messages.
            # token table isn't created

    #METHODS TO CREATE AND POPULATE A DATABASE USING DIFFERENT SCRIPTS
    def create_tables(self, schema=None):
        '''
        Create programmatically the tables from a schema file.

        :param schema: path to the .sql schema file. If this parmeter is
            None, then *db/forum_schema_dump.sql* is utilized.

        '''
        con = sqlite3.connect(self.db_path)
        if schema is None:
            schema = DEFAULT_SCHEMA
        try:
            with open(schema) as f:
                sql = f.read()
                cur = con.cursor()
                cur.executescript(sql)
        finally:
            con.close()

    def populate_tables(self, dump=None):
        '''
        Populate programmatically the tables from a dump file.

        :param dump:  path to the .sql dump file. If this parameter is
            None, then *db/chirrup_data_dump.sql* is utilized.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        #Populate database from dump
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        with open (dump) as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)
