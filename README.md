<p align=center><img src=_src/assets/banner.png><p>

# <h1 align=center> **Automatic loading of MySQL Workbench with CSV and/or Excel files** </h1>


## Introduction

Script to create MySQL DB based on CSV and/or Excel files. It also create a `sql` script file.


## Requirement

In order to run the code, the following libraries must be installed:

- Pandas (`python -m pip install pandas`)
- Mysql-connector (`python -m pip install mysql-connector-python`)
- openpyxl (`python -m pip install openpyxl`)
- xlrd (`python -m pip install xlrd`)


## Run code

The script can be run with some parameters:

- -t: Workbench hostname (default: localhost)
- -u: Workbench username (default: root)
- -d: Database name (default: db_test)

Example
```
python3 load2SQL.py -d 'test'
```


## Folders

The `loadFiles` folder will contain all the `csv`, `xls` and `xlsx` files to be converted to `csv` extension.
In case this folder does not exist, it should be created.<br>
In the `csvFiles` will be created automatically and it will contain all the `csv` files.
Those file will be copied to the respective folder in order to be recognized for Workbench and load them correctly.<br>


## Password

The user has to create a `pass.json` file with the following content:

```
{
    "workbench": "password",
    "linux": "password\n"
}
```

Please complete the password with your own password, otherwise the script will crush. In case Windows OS, linux admin password is not required, but you should not delete the tag `linux`.


## WINDOWS SYSTEM TROUBLESHOOT

In case the following error appear in Windows OS

```
Error: '1290 (HY000): The MySQL server is running with the --secure-file-priv option so it cannot execute this statement'
```

Uncomment the following line in the `load_2_mysql.py` file.

```
path_to_csv = fr'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Data\\{db_name}\\'
```

Then, in Windows system, go to the following path:

```
C:\ProgramData\MySQL\MySQL Server 8.0
```

Open the file `my.ini` and replace the line:

```
secure-file-priv="C:/ProgramData/MySQL/MySQL Server 8.0/Uploads"
```

By the following line:

```
secure-file-priv=""
```

Save the file and restart `MySQL80` service. To do so, got to Task manager -> Services tag, find `MySQL80`, right click and choose Restart option.