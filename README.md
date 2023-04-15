# CreateMySQLwithCSV

Script to create MySQL DB based based on CSV or Excel files.

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

The `loadFiles` folder will contain all the `csv`, `xls` and `xlsx` files to be converted to `csv` extension. In case this folder does not exist, it should be created.<br>
In the `csvFiles` will be copied all the `csv` files and then, those file will be copied to the respective folder in order to be recognized for Workbent to be loaded. In case this folder does not exist, it should be created.<br>

## Password

The user has to create a `pass.json` file with the following content:

```
{
    "workbench": "password",
    "linux": "password\n"
}
```

Please complete the password with your own password, otherwise the script will crush. In case Windows OS, linux admin password is not required.