"""Module providing file insertion to mysql database."""
import os
import sys
import subprocess
import platform
import shutil
import re
import argparse
import json
import pandas as pd

from mysql_lib import MySQL_Class


def get_path(os_var=''):
    """Get path to read and store csv files.

    Args:
        os_var (str): Operating system.

    Returns:
        (str): Folder to load files.
        (str): Folder to store csv files.
    """
    csv_path = ''
    load_path = ''

    if 'linux' in str.lower(os_var):
        load_path = 'loadFiles/'
        csv_path = 'csvFiles/'
    elif 'win' in str.lower(os_var):
        load_path = 'loadFiles\\'
        csv_path = 'csvFiles\\'
    else:
        print('No Operating System detected')
        sys.exit(0)

    return load_path, csv_path


def create_csv_store_path(csv_path=''):
    """Create folder to store csv files if not exist.

    Args:
        csv_path (str): Path where CSV files will be stored.
    """
    is_exist = os.path.exists(csv_path)
    if not is_exist:
        try:
            os.makedirs(csv_path)
        except FileExistsError:
            print(f'Cannot create {csv_path}')
            sys.exit(0)


def convert_file_to_csv(file_list=None, load_path='', csv_path=''):
    """Convert xls file to csv and store csv files to new folder.

    Args:
        file_list (list): File list that contains csv and/or excel files.
        load_path (str): Path that contains files to be converted.
        csv_path (str): Path where CSV files will be stored.
    """
    for file in file_list:
        if '.xls' in file:
            try:
                df_data = pd.read_excel(load_path + file)
                newfile, _ = file.split('.')
                df_data.to_csv(csv_path + newfile.capitalize() + '.' + 'csv',
                               index=None, header=True)
            except Exception as error:
                print(error)
                print(f'Fail to open {load_path}{file}')
                sys.exit(0)
        elif '.csv' in file:
            try:
                shutil.copyfile(load_path + file, csv_path + file)
            except Exception as error:
                print(error)
                print(f'Fail to copy {load_path}{file} to {csv_path}')
                sys.exit(0)


def get_column_from_csv(csv_table_files=None, separator_list=None, column_list=None, csv_path=''):
    """Get column names list from csv files

    Args:
        csv_table_files (list): File list that contains csv files.
        separator_list (list): List where separator will be stored.
        column_list (list): List where csv columns will be stored.
        csv_path (str): Path where CSV files are stored.
    """
    for csv_file in csv_table_files:
        with open(csv_path + csv_file, 'r', encoding='UTF-8') as file:
            regex = '[,;|-]'
            aux_var = file.readline().strip()
            column = re.split(regex, aux_var)
            index = re.search(regex, aux_var).start()
            separator_list.append(aux_var[index])
            column_list.append(column)


def check_unknow_char(column_list=None):
    """Check for unknow characters when files are not UTF-8

     Args:
        column_list (list): Column list to be returned.
    """
    for index, column in enumerate(column_list):
        col = []
        for item in column:
            if '\ufeff' in item:
                item = item.replace('\ufeff', '')
            col.append(item)
        column_list[index] = col


def get_query_table(csv_table_files=None, column_list=None, query_list=None):
    """Get queries to create tables

    Args:
        csv_table_files (list): File list that contains csv files.
        column_list (list): List where csv columns are stored.
        query_list (list): List of query to create MySQL table.
    """
    for file, elements in zip(csv_table_files, column_list):
        table, _ = file.split('.')
        var_table = f'CREATE TABLE IF NOT EXISTS {table} ('
        for index, item in enumerate(elements):
            item = item.capitalize()
            if item.lower().startswith('id'):
                var_table += f'{item} INT'
            elif 'fecha' in item.lower():
                var_table += f'{item} DATE'
            else:
                var_table += f'{item} VARCHAR(200)'
            if index != len(elements) - 1:
                var_table += ','
        var_table += ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;'
        query_list.append(var_table)


def get_passwords():
    """Get Workbench and sudo passwords from internal file

    Returns:
        (str): Database Workbench password.
        (str): Linux admin password.
    """
    pass_file = 'pass.json'
    try:
        with open(pass_file, 'r', encoding='UTF-8') as file:
            data = json.load(file)
            pass_db = data["workbench"]
            pass_sudo = data["linux"]
    except FileNotFoundError:
        print(f'The {pass_file} file does not exist. Please read the README.md file')
        sys.exit(0)

    return pass_db, pass_sudo


def run():
    """Execute the code to convert csv files into MySQL database"""
    column_list = []
    separator_list = []
    query_list = []
    path_to_csv = ''

    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('-t', '--host_name', metavar='<host_name>', type=str, required=False,
                            default='localhost', help='Workbench hostname', dest='host_name')
    arg_parser.add_argument('-u', '--user_name', metavar='<user_name>', type=str, required=False,
                            default='root', help='Workbench username', dest='user_name')
    arg_parser.add_argument('-d', '--database', metavar='<database>', type=str, required=False,
                            default='test_db', help='Database name', dest='db_name')

    args = arg_parser.parse_args()

    db_name = args.db_name
    os_var = platform.system()

    # Get path for storing and reading csv file
    load_path, csv_path = get_path(os_var=os_var)


    # Create csv_path directory if not exist
    create_csv_store_path(csv_path=csv_path)

    file_list = os.listdir(load_path)

    # Convert xls file to csv and copy files to new folder
    convert_file_to_csv(file_list=file_list, load_path=load_path, csv_path=csv_path)

    file_list = os.listdir(csv_path)

    # Get CSV files
    csv_table_files = [file for file in file_list if 'csv' in file]

    # Get column and return list of column and separators
    get_column_from_csv(csv_table_files=csv_table_files, separator_list=separator_list,
                        column_list=column_list, csv_path=csv_path)

    # Check for unknow characters when files are not UTF-8 and return value in clolumn_list
    check_unknow_char(column_list=column_list)

    # Get queries to create tables, return value in query_list
    get_query_table(query_list=query_list, csv_table_files=csv_table_files, column_list=column_list)

    # Get Workbench and super user Linux password passwords to copy file as admin
    pass_db, pass_sudo = get_passwords()

    # Connect to mySQL data base
    connection = MySQL_Class(password=pass_db)

    # Create database if not exist
    create_database_query = f'CREATE DATABASE IF NOT EXISTS {db_name}'
    connection.create_database(create_database_query)

    # Create to the data base
    connection.create_db_connection(db_name) # Connect to the Database

    # create tables
    for element in query_list:
        connection.execute_query(element)

    query = 'set global local_infile=true;'
    connection.execute_query(query)

    # Copy files to the mysql folder
    if 'linux' in str.lower(os_var):
        path_to_csv = f'/var/lib/mysql/{db_name}/'
        # Copy file to OS folder to import tables
        try:
            for file in csv_table_files:
                cmd = ['sudo', 'cp', csv_path + file, path_to_csv]
                pw2 = pass_sudo.encode()
                subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE).communicate(input=pw2)
        except Exception as error:
            print(error)
            print(f'Some errors occur during the copy file process in {os_var} system. '\
                  'Please read the README.md file')
            sys.exit(0)
    elif 'win' in str.lower(os_var):
        try:
            path_to_csv = r'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\'
            for file in csv_table_files:
                shutil.copyfile(csv_path + file, path_to_csv + file)
        except Exception as error:
            print(error)
            print(f'Some errors occur during the copy file process in {os_var} system. ' \
                  'Please read the README.md file')
            sys.exit(0)
    else:
        print('No Operating System detected')
        sys.exit(0)

    # fill tables
    for file, separator, columns in zip(csv_table_files, separator_list, column_list):
        table, _ = file.split('.')
        column_field = '(' + ','.join(columns) + ')'

        # print(column_field)
        query = f"LOAD DATA INFILE '{file}' INTO TABLE {table} " \
                f"FIELDS TERMINATED BY '{separator}' ENCLOSED BY '' ESCAPED BY '' " \
                f"LINES TERMINATED BY '\n' IGNORE 1 LINES {column_field};"

        print(f'Tabla: {table}')
        connection.execute_query(query) #


# Driver Code
if __name__ == '__main__' :

    # Start script
    print('Create Database\n')

    # calling run function
    run()
