from mysql_lib import MySQL_Class
import os
import pandas as pd
import re
import shutil
import platform
import json
import subprocess
import argparse


def run():

    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('-t', '--host_name', metavar='<host_name>', type=str, required=False,
                            default='localhost', help='Workbench hostname', dest='host_name')
    arg_parser.add_argument('-u', '--user_name', metavar='<user_name>', type=str, required=False,
                            default='root', help='Workbench username', dest='user_name')
    arg_parser.add_argument('-d', '--database', metavar='<database>', type=str, required=False,
                            default='db_test', help='Database name', dest='db_name')

    args = arg_parser.parse_args()

    db_name = args.db_name
    load_path = 'loadFiles/'
    csv_path = 'csvFiles/'
    pass_file = 'pass.json'

    dir_list = os.listdir(load_path)

    # Convert xls file to csv and copy files to new folder
    for file in dir_list:
        if '.xls' in file:
            try:
                df = pd.read_excel(load_path + file)
                newfile, ext = file.split('.')
                df.to_csv(csv_path + newfile.capitalize() + '.' + 'csv', index=None, header=True)
            except:
                print(f'Fail to open {load_path}{file}')
                exit(0)
        elif '.csv' in file:
            try:
                shutil.copyfile(load_path + file, csv_path + file)
            except:
                print(f'Fail to copy {load_path}{file} to {csv_path}')
                exit(0)

    column_list = []
    dir_list = os.listdir(csv_path)

    # Get CSV files
    csv_table_files = [file for file in dir_list if 'csv' in file]

    separator_list = []

    # Get column
    for file in csv_table_files:
        with open(csv_path + file, 'r', encoding='UTF-8') as f:
            regex = '[,;|-]'
            aux_var = f.readline().strip()
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
        table, ext = file.split('.')
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
                var_table += f','
        var_table += f') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;'
        query_list.append(var_table)


    # Get Workbench and sudo passwords from internal file
    try:
        with open(pass_file, 'r') as file:
            data = json.load(file)
            pass_db = data["workbench"]
            pass_sudo = data["linux"]
    except:
        print(f'The {pass_file} doe not exist. Please read the README.md file')
        exit(0)

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

    # Get OS
    os_var = platform.system()
    path_to_csv = ''
    if 'linux' in str.lower(os_var):
        path_to_csv = f'/var/lib/mysql/{db_name}/'
        # Copy file to OS folder to import tables
        try:
            for file in csv_table_files:
                cmd = ['sudo', 'cp', csv_path + file, path_to_csv]
                pw2 = pass_sudo.encode()
                proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE).communicate(input=pw2)
        except:
            print(f'Some errors occur during the copy file process in {os_var} system. Please read the README.md file')
            exit(0)
    elif 'win' in str.lower(os_var):
        try:
            path_to_csv = r'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\'
            for file in csv_table_files:
                shutil.copyfile(csv_path + file, path_to_csv + file)
        except:
            print(f'Some errors occur during the copy file process in {os_var} system. Please read the README.md file')
            exit(0)
    else:
        print('No Operating System detected')
        exit(0)

    # fill tables
    for file, separator, columns in zip(csv_table_files, separator_list, column_list):
        table, ext = file.split('.')
        column_field = '(' + ','.join(columns) + ')'

        # print(column_field)
        query = f"LOAD DATA INFILE '{file}' INTO TABLE {table} " \
                f"FIELDS TERMINATED BY '{separator}' ENCLOSED BY '' ESCAPED BY '' LINES TERMINATED BY '\n' " \
                f"IGNORE 1 LINES {column_field};"

        print(f'Tabla: {table}')
        connection.execute_query(query) #


# Driver Code
if __name__ == '__main__' :

    # Start script
    print('Create Database\n')

    # calling run function
    run()
