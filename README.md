# CreateMySQLwithCSV

Script to create MySQL DB based on CSV or Excel files.


## Requirement

In order to run the code, the following libraries must be installed:

- Pandas (`python -m pip install pandas`)
- Mysql-connector (`python -m pip install mysql-connector`)
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