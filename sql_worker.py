import sqlite3
from config import DATABASE

class sql_worker:

    def create_t(self, name, *args):
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        vals = ""
        for i in args:
            vals += i + ","
        cur.execute(f"CREATE TABLE IF NOT EXIST {name}({args[:-1]}")
        con.close()
    
    def insert(self, name, **kwargs):
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        vals = ""
        for i,j in enumerate(kwargs):
            vals += i + "=" + j + ","
        cur.execute(f"INSERT INTO {name} VALUES({vals[:-1]})")
        con.close()

    def change(self, name, where = {}, *args,**kwargs):
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        vals = ""
        for i, j in enumerate(args):
            vals += i + "=" + j + ","
        vals = vals[:-1]
        for i,j in enumerate(kwargs):
            vals += i + "=" + j + ","
        cur.execute(f"UPDATE {name} SET {vals[:-1]} WHERE {where.keys()[0]} = {where[where.keys()[0]]}")
        con.close()


    def execute(self, command):
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute(command)
        con.close()
    
    def get(self, command):
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        res = cur.execute(command)
        con.close()
        return(res)
