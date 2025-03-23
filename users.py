from sql_worker import sql_worker
from user import user
from config import USERS_TABLE_NAME

"""
Написать создание юзеров
обмен деньгами/акциями(бля акции)
Создание таблицы
"""

class users_manager:
    
    def __init__(self):
        self.sql_worker.create_t(self.table, "user_id", "name", "capital", "team", "is_admin")
    
    def create_user(self, is_admin=0, **kwargs):
        new_user = user(is_admin, **kwargs)
        self.users.append(new_user)

    def transfer(self, user_from, user_to, val):
        
        for user in self.users:
            if user.get_name() == user_from:
                user_from = user
            elif user.get_name() == user_to:
                user_to = user
        if type(user_to) is str:
            raise ValueError("Пользователь не найден")
        elif type(user_from) is str:
            raise ValueError("Ты кто блять?!?!")
        else:
            try:
                user_from.change_capital(-val)
            except ValueError:
                raise ValueError("Нехвадка средств")
            user_to.change_capital(val)
            
     
        


    users = []
    sql_worker = sql_worker()
    table = USERS_TABLE_NAME