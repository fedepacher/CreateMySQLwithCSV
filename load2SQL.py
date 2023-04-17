from mysql_lib import MySQL_Class
import os
import pandas as pd
import re
import shutil
import platform
import json
import subprocess
import argparse
import sys


def run():

    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('-t', '--host_name', metavar='<host_name>', type=str, required=False,
                            default='localhost', help='Workbench hostname', dest='host_name')
    arg_parser.add_argument('-u', '--user_name', metavar='<user_name>', type=str, required=False,
                            default='root', help='Workbench username', dest='user_name')
    arg_parser.add_argument('-d', '--database', metavar='<database>', type=str, required=False,
                            default='test_db', help='Database name', dest='db_name')

    args = arg_parser.parse_args()

    db_name = args.db_name
    # Get OS
    os_var = platform.system()
    if 'linux' in str.lower(os_var):
        load_path = 'loadFiles/'
        csv_path = 'csvFiles/'
    elif 'win' in str.lower(os_var):
        load_path = 'loadFiles\\'
        csv_path = 'csvFiles\\'
    else:
        print('No Operating System detected')
        sys.exit(0)

    # Create csv_path directory if not exist
    is_exist = os.path.exists(csv_path)
    if not is_exist:
        try:
            os.makedirs(csv_path)
        except FileExistsError:
            print(f'Cannot create {csv_path}')
            sys.exit(0)

    pass_file = 'pass.json'

    dir_list = os.listdir(load_path)

    # Convert xls file to csv and copy files to new folder
    for file in dir_list:
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

    column_list = []
    dir_list = os.listdir(csv_path)

    # Get CSV files
    csv_table_files = [file for file in dir_list if 'csv' in file]

    separator_list = []

    # Get column
    for csv_file in csv_table_files:
        with open(csv_path + csv_file, 'r', encoding='UTF-8') as file:
            regex = '[,;|-]'
            aux_var = file.readline().strip()
            column = re.split(regex, aux_var)
            index = re.search(regex, aux_var).start()
            separator_list.append(aux_var[index])
            column_list.append(column)

    # Check for unknow characters when files are not UTF-8
    for index in range(len(column_list)):
        col = []
        for column in column_list[index]:
            if '\ufeff' in column:
                column = column.replace('\ufeff', '')
            col.append(column)
        column_list[index] = col

    # Get queries to create tables
    query_list = []
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


    # Get Workbench and sudo passwords from internal file
    try:
        with open(pass_file, 'r', encoding='UTF-8') as file:
            data = json.load(file)
            pass_db = data["workbench"]
            pass_sudo = data["linux"]
    except Exception as error:
        print(error)
        print(f'The {pass_file} doe not exist. Please read the README.md file')
        sys.exit(0)

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
    path_to_csv = ''
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
