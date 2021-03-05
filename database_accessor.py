import sqlite3
from sqlite3 import Error



class database:


    def __init__(self):

        # sql to create default players table
        sql_to_create_account_table= '''CREATE TABLE IF NOT EXISTS players (
    user_id integer PRIMARY KEY,
    total_xp integer NOT NULL,
    guild_id integer NOT NULL
    )
    '''
        try:
            # create connection
            self.conn = sqlite3.connect('database.db')

            c = self.conn.cursor()
            c.execute(sql_to_create_account_table)
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

    def add_xp(self, xp_to_add, account_id,guild_id):

        sql_to_select_account = 'SELECT * FROM players WHERE user_id = ? AND guild_id = ?'

        cur = self.conn.cursor()
        # find account to update
        cur.execute(sql_to_select_account, (account_id,guild_id))
        account = cur.fetchall()
        # if account exists
        if account:
            # find first account listed, and get second column to get xp
            new_xp = account[0][1] + xp_to_add

            sql_to_update = '''UPDATE players
                               SET total_xp = ?
                               WHERE user_id = ? AND guild_id = ?
            '''

            updated_account = (new_xp, account_id, guild_id)

            cur.execute(sql_to_update,updated_account)

            self.conn.commit()
        else:
            # if account doesn't exist
            self.new_account(account_id,guild_id,xp=xp_to_add)

    def get_xp(self,account_id,guild_id):
        sql_to_select_account = 'SELECT * FROM players WHERE user_id = ? AND guild_id = ?'

        cur = self.conn.cursor()
        # find account to update
        cur.execute(sql_to_select_account, (account_id,guild_id))
        account =cur.fetchall()
        try:
            return account[0][1]

        except IndexError:
            self.new_account(account_id,guild_id)
            return 0 
        

        
        




