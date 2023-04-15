import mysql.connector
from mysql.connector import Error


class MySQL_Class:

    def __init__(self, host_name='localhost', user_name='root', password=''):
        self._host_name = host_name
        self._user_name= user_name
        self._password = password
        self.create_server_connection(self._host_name, self._user_name, self._password)


    def create_server_connection(self, host_name, user_name, user_password):
        self._connection = None
        try:
            self._connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                auth_plugin='mysql_native_password'
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")

        return self._connection

    def create_db_connection(self, db_name):
        self._connection = None
        try:
            self._connection = mysql.connector.connect(
                host=self._host_name,
                user=self._user_name,
                passwd=self._password,
                database=db_name,
                auth_plugin='mysql_native_password'
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")

        return self._connection

    def create_database(self, query):
        self._cursor = self._connection.cursor()
        try:
            self._cursor.execute(query)
            print("Database created successfully")
        except Error as err:
            print(f"Error: '{err}'")


    def execute_query(self, query):
        self._cursor = self._connection.cursor()
        try:
            self._cursor.execute(query)
            self._connection.commit()
            print("Query successful")
        except Error as err:
            print(f"Error: '{err}'")


    def execute_list_query(self, sql, val):
        self._cursor = self._connection.cursor()
        try:
            self._cursor.executemany(sql, val)
            self._connection.commit()
            print("Query successful")
        except Error as err:
            print(f"Error: '{err}'")


    def read_query(self, query):
        self._cursor = self._connection.cursor()
        result = None
        try:
            self._cursor.execute(query)
            result = self._cursor.fetchall()
            return result
        except Error as err:
            print(f"Error: '{err}'")