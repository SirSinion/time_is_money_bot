from sql_worker import sql_worker
from config import ACTIVS_TABLE_NAME
class market:

    def __init__(self, *args, **kwargs): # На старте принимает args - столбцы и kwargs - станция : цена
        for colum in args:
            self.colums.append(colum)
        for blank, cost in enumerate(kwargs):
            self.blanks[blank] = cost
        self.sql_worker.create_t(self.t_name, *args)
        self._update()

    def _update(self): # Функция для обновления бд, после изменения класса
        for blank, value in enumerate(self.blanks):
            self.sql_worker.change(self.t_name,{f"{self.colums[0]}": f"{blank}"}, {f"{self.colums[1]}": f"{value}"} )

    def upload(self, **kwargs):#Для изменения значения на %, принимает станция - 70%
        for blank, procent in enumerate(kwargs):
            self.blanks[blank] = self.blanks[blank] + self.blanks[blank] * procent/100
        self._update()

    def val_change(self, **kwargs):#Прямое изменение значения
        for blank, value in enumerate(kwargs):
            self.blanks[blank] = value
        self._update()
        
    colums = []
    sql_worker = sql_worker()
    t_name = ACTIVS_TABLE_NAME
    blanks = {}
    
    