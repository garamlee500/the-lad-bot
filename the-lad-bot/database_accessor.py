import sqlite3
from sqlite3 import Error


class Database:

    def __init__(self):

        # sql to create default players table
        sql_to_create_account_table = '''CREATE TABLE IF NOT EXISTS players (
    user_id integer NOT NULL,
    total_xp integer NOT NULL,
    guild_id integer NOT NULL,
    record_id integer PRIMARY KEY
    )
    '''

        sql_to_create_auto_role = '''CREATE TABLE IF NOT EXISTS autoroles (


    role_id integer PRIMARY KEY,
    minimum_level integer NOT NULL,
    guild_id integer NOT NULL
    )
    '''

        sql_to_create_react_role = '''CREATE TABLE IF NOT EXISTS reactroles (
     
    message_id integer PRIMARY KEY,
    role_id integer NOT NULL
    )    
    '''
        try:
            # create connection
            self.conn = sqlite3.connect('database.db')

            c = self.conn.cursor()
            c.execute(sql_to_create_account_table)
            c.execute(sql_to_create_auto_role)
            c.execute(sql_to_create_react_role)

        except Error as e:
            print(e)

    def new_account(self, account_id, guild_id, xp=0):
        # create account
        account = (account_id, xp, guild_id)
        cur = self.conn.cursor()

        sql_to_create_account = '''INSERT INTO players(user_id,total_xp,guild_id)
                                   VALUES(?,?,?)
        '''
        cur.execute(sql_to_create_account, account)
        self.conn.commit()

    def add_xp(self, xp_to_add, account_id, guild_id):

        sql_to_select_account = 'SELECT * FROM players WHERE user_id = ? AND guild_id = ?'

        cur = self.conn.cursor()
        # find account to update
        cur.execute(sql_to_select_account, (account_id, guild_id))
        account = cur.fetchall()
        # if account exists
        if account:
            # find first account listed, and get second column to get xp
            new_xp = account[0][1] + xp_to_add

            # if new_xp is less than 0 make it 0 mf

            if new_xp < 0:
                new_xp = 0

            sql_to_update = '''UPDATE players
                               SET total_xp = ?
                               WHERE user_id = ? AND guild_id = ?
            '''

            updated_account = (new_xp, account_id, guild_id)
            cur.execute(sql_to_update, updated_account)

            self.conn.commit()
            return new_xp
        else:
            # if account doesn't exist
            self.new_account(account_id, guild_id, xp=xp_to_add)
            return xp_to_add

    def get_xp(self, account_id, guild_id):
        sql_to_select_account = 'SELECT * FROM players WHERE user_id = ? AND guild_id = ?'

        cur = self.conn.cursor()
        # find account to update
        cur.execute(sql_to_select_account, (account_id, guild_id))
        account = cur.fetchall()
        try:
            return account[0][1]

        except IndexError:
            self.new_account(account_id, guild_id)
            return 0

    def get_all_from_guild(self, guild_id):
        sql_to_select_accounts = 'SELECT * FROM players WHERE guild_id=?'

        cur = self.conn.cursor()

        cur.execute(sql_to_select_accounts, (guild_id,))

        accounts = cur.fetchall()

        # automatically sort accounts

        def get_key(item):
            return item[1]

        accounts = sorted(accounts, key=get_key)[::-1]
        return accounts

    def create_new_auto_role(self, role_id, minimum_level, guild_id):
        # create auto role
        autorole = (role_id, minimum_level, guild_id)
        cur = self.conn.cursor()

        # This SQL will delete a record and replace it if it is present
        sql_to_create_autorole = '''REPLACE INTO autoroles(role_id,minimum_level,guild_id)
                                   VALUES(?,?,?)
        '''
        cur.execute(sql_to_create_autorole, autorole)
        self.conn.commit()

    # Get autoroles for guild
    def autorole_guild(self, guild_id):
        sql_to_select_autorole = 'SELECT * FROM autoroles WHERE guild_id = ?'

        cur = self.conn.cursor()
        # find autorole to update
        cur.execute(sql_to_select_autorole, (guild_id,))
        autoroles = cur.fetchall()

        # automatically sort records

        def get_key(item):
            return item[1]

        autoroles = sorted(autoroles, key=get_key)[::-1]
        return autoroles

    def remove_autorole(self, role_id, guild_id):
        sql_to_delete_autorole = 'DELETE FROM autoroles WHERE role_id = ? AND guild_id = ?'

        cur = self.conn.cursor()
        cur.execute(sql_to_delete_autorole, (role_id, guild_id))
        self.conn.commit()

    def create_reactrole(self, message_id, role_id):

        cur = self.conn.cursor()

        sql_to_create_reactrole = '''INSERT INTO reactroles(message_id, role_id)
                                   VALUES(?,?)
        '''
        cur.execute(sql_to_create_reactrole, (message_id, role_id))
        self.conn.commit()

    def find_reactrole(self, message_id):
        sql_to_select_reactrole = 'SELECT * FROM reactroles WHERE message_id = ?'

        cur = self.conn.cursor()
        # find autorole to update
        cur.execute(sql_to_select_reactrole, (message_id,))
        reactroles = cur.fetchall()

        return reactroles