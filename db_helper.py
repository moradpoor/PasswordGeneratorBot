import os
from config import DB_NAME , path
import sqlite3
class DBHelper():
    def __init__(self):
        self.dbname = path + DB_NAME
        self.conn = sqlite3.connect(self.dbname, check_same_thread=False)
    def setup(self):
        personals = 'CREATE TABLE IF NOT EXISTS personals (chat_id INTEGER, ban INTEGER, start_date TEXT)'
        passwords = 'CREATE TABLE IF NOT EXISTS passwords (chat_id INTEGER ,user TEXT,password TEXT, title TEXT,description TEXT)'
        self.conn.execute(passwords)
        self.conn.execute(personals)
        self.conn.commit()

    def NewUser(self,chat_id):
        stmt = 'SELECT chat_id FROM personals'
        personals = [x[0] for x in self.conn.execute(stmt)]
        return True if chat_id not in personals else False
    def AddNewUser(self,chat_id,start_date):
        if self.NewUser(chat_id):
            stmt = 'INSERT INTO personals (chat_id,ban,start_date) VALUES (?,?,?)'
            args = (chat_id,0,start_date)
            self.conn.execute(stmt,args)
            self.conn.commit()
    def NewPassword(self,chat_id,password,title,description):
        stmt = 'INSERT INTO passwords VALUES (?,?,?,?,?)'
        args = (chat_id,None,password,title,description)
        self.conn.execute(stmt,args)
        self.conn.commit()
    def DeletePassword(self,chat_id,password):
        stmt = 'DELETE FROM passwords WHERE chat_id=(?) AND password=(?)'
        args = (chat_id,password)
        self.conn.execute(stmt,args)
        self.conn.commit()
    def GetMyPasswords(self,chat_id):
        stmt = 'SELECT * FROM passwords WHERE chat_id=(?)'
        args = (chat_id,)
        return [x for x in self.conn.execute(stmt,args)]
    def GetPasswordByTitle(self,chat_id,title):
        stmt = 'SELECT password FROM passwords WHERE chat_id=(?) AND title=(?)'
        args = (chat_id,title)
        return [x for x in self.conn.execute(stmt,args)]
    def DeleteAllPasswords(self,chat_id):
        self.conn.execute(f"DELETE FROM passwords WHERE chat_id={chat_id}")
        self.conn.commit()

