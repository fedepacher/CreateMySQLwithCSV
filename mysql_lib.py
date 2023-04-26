"""Module providing function mysql database connection."""
import sys
import mysql.connector
from mysql.connector import Error


class MySQLClass:
    """Class to encapsulate MySQL method"""

    def __init__(self, host_name='localhost', user_name='root', password='', logging=''):
        """Constructor of the class.

        Args:
            host_name (str): Database hostname.
            user_name (str): Database username.
            user_password (str): Database password.
            logging (logging): Logging object.
        """
        self._host_name = host_name
        self._user_name= user_name
        self._password = password
        self._connection = None
        self._cursor = None
        self._logging = logging
        self.create_server_connection(self._host_name, self._user_name, self._password)


    def create_server_connection(self, host_name, user_name, user_password):
        """Create a server connection.

        Args:
            host_name (str): Database hostname.
            user_name (str): Database username.
            user_password (str): Database password.

        Returns:
            mysql.connector.connection.MySQLConnection: Connection object.
        """
        try:
            self._connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                auth_plugin='mysql_native_password'
            )
            self._logging.info("MySQL Database connection successful")
        except Error as err:
            self._logging.error("Error: '%s'", err)
            sys.exit(0)

        return self._connection

    def create_db_connection(self, db_name):
        """Create a database connection.

        Args:
            db_name (str): Database name.

        Returns:
            mysql.connector.connection.MySQLConnection: Connection object.
        """
        try:
            self._connection = mysql.connector.connect(
                host=self._host_name,
                user=self._user_name,
                passwd=self._password,
                database=db_name,
                auth_plugin='mysql_native_password'
            )
            self._logging.info("MySQL Database connection successful")
        except Error as err:
            self._logging.error("Error: '%s'", err)
            sys.exit(0)

        return self._connection

    def create_database(self, query):
        """Create a database.

        Args:
            query (str): Query to create database.
        """
        self._cursor = self._connection.cursor()
        try:
            self._cursor.execute(query)
            self._logging.info("Database created successfully")
        except Error as err:
            self._logging.error("Error: '%s'", err)
            sys.exit(0)


    def execute_query(self, query):
        """Execute the query to the database.

        Args:
            query (str): Query to create database.
        """
        self._cursor = self._connection.cursor()
        try:
            self._cursor.execute(query)
            self._connection.commit()
            self._logging.info("Query successful")
        except Error as err:
            self._logging.error("Error: '%s'", err)
            sys.exit(0)


    def execute_list_query(self, sql, val):
        """Execute a list of query to the database. It is used to insert values to the database

        Example:
            sql = '''
                INSERT INTO teacher (teacher_id, first_name, last_name, language_1, language_2,
                dob, tax_id, phone_no) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                '''
            val = [
                (7, 'Hank', 'Dodson', 'ENG', None, '1991-12-23', 11111, '+491772345678'),
                (8, 'Sue', 'Perkins', 'MAN', 'ENG', '1976-02-02', 22222, '+491443456432')
            ]

        Args:
            sql (str): Query to excecute in the database.
            val (list of list): List of value to be executed in the query.
        """
        self._cursor = self._connection.cursor()
        try:
            self._cursor.executemany(sql, val)
            self._connection.commit()
            self._logging.info("Query successful")
        except Error as err:
            self._logging.error("Error: '%s'", err)
            sys.exit(0)


    def read_query(self, query):
        """Read value of the database.

        Args:
            query (str): Query to read database.
        """
        self._cursor = self._connection.cursor()
        result = None
        try:
            self._cursor.execute(query)
            result = self._cursor.fetchall()
            self._logging.info("Query read successful")
            return result
        except Error as err:
            self._logging.error("Error: '%s'", err)
            sys.exit(0)
