import psycopg2
from config import *


class DB():

    def __init__(self):
        self._name = name
        self._connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)

    def __get_column(self):
        connection = self._connection
        with connection.cursor() as cursor:
            cursor.execute(
                f'''SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = '{self._name}'
                    ORDER BY ordinal_position;'''
            )
            column = [i[0] for i in cursor.fetchall()]
            return column

    def add(self, data: list):
        connection = self._connection
        column = str()
        info = str()
        for key, value in zip(self.__get_column(), data):
            column += ', ' + str(key)
            info += ', ' + "'"+str(value)+"'"

        with connection.cursor() as cursor:
            cursor.execute(
                f"""insert into {self._name} ({column[2:]}) values ({info[2:]})"""
            )
            connection.commit()

    def delete(self, data: str):
        connection = self._connection
        username = str()
        with connection.cursor() as cursor:
            cursor.execute(
                f""" select username from {self._name} where first_name = '{data}'"""
            )
            username = cursor.fetchall()[0][0]
        with connection.cursor() as cursor:
            cursor.execute(
                f"""delete from {self._name} where username = '{username}'"""
            )
            connection.commit()

    def update(self, data: dict):
        connection = self._connection

        set_clause = ', '.join([f"{key} = '{value}'" for key, value in data.items()])

        with connection.cursor() as cursor:
            cursor.execute( f"""
                UPDATE {self._name} 
                SET {set_clause} 
                WHERE username = '{data['username']}'
            """)
            connection.commit()

    def find(self, data: dict):
        connection = self._connection
        info = ' and '.join([f"{key} ='{value}'" for key, value in data.items()])
        with connection.cursor() as cursor:
            cursor.execute(
                f"""select * from {self._name} where {info}"""
            )
            return True if cursor.fetchall() != [] else False

    def get_users(self):
        connection = self._connection
        users = []
        column = self.__get_column()
        with connection.cursor() as cursor:
            cursor.execute(
                f"""select * from {self._name}"""
            )
            for row in cursor.fetchall():
                data = {}
                for i, j in zip(row, column):
                    data[j] = i
                users.append(data)
            return users
db = DB()

#db.add(['123','123','123','ddd@gmail.com','123'])
#db.delete({'username': '123'})
#db.update({'last_name': 'kosparov', 'username': 'chicha', 'email': '123@gmail.com', 'password': '24653'})
#print(db.get_users())
#print(db.find_user(['123', '123']))
#print(db.find({'username': '09'}))
