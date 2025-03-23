from sql_worker import sql_worker
from config import USERS_TABLE_NAME

class user:

    def _upload(self):
        self.sql_worker.change(self.table,{ "user_id" : self.info["user_id"] }, self.info)

    def change_capital(self, value):
        if self.info['capital'] + value < 0 and self.info['is_admin'] == 0:
            raise ValueError("Нехватает средств")
        else:
            self.info['capital'] += value
            self._upload()

    def change_name(self, new_name):
        self.info['name'] = new_name
        self._upload()

    def get_id(self):
        return(self.info["user_id"])
    
    def get_name(self):
        return(self.info["name"])

    def __init__(self, admin = 0, **kwargs):
        for i, j in enumerate(kwargs):
           if i in self.info.keys():
               self.info[i] = j
        if admin:
            self.info['is_admin'] = 1
        else:
            self.info['is_admin'] = 0
        self._upload()
    
    

    info = {"user_id": None,
            "name": None,
            "capital": None,
            "team": None,
            "is_admin": 0}
    sql_worker = sql_worker()
    table = USERS_TABLE_NAME

    