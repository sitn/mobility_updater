# Shared mobility updater

## Requirements

Python 3.6+

## Install

* Get the code and create the virtual environment:

```
git clone https://github.com/sitn/mobility_updater.git
cd mobility_updater
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

* Copy-paste the `config.yml.sample` file
* Rename it to `config.yml`
* Use the `create_table.sql`, adapt the table name and schema if necessary

That's it!

## Run it

With _cmd_ or _powershell_, `cd` to your `shared_mobility_updater` folder and:

1. For the shared mobility part:

```
venv\Scripts\python shared_mobility.py
```

2. For the electric stations part:

```
venv\Scripts\python electric_mobility.py
```

## Purpose

The `shared_mobility.py` script gets data from the national shared mobility platform.
The explanation can be found [here](https://github.com/SFOE/sharedmobility)

The `electric_mobility.py` script gets data from the national data infrastructure For electromobility:
- Data access is described [here](https://github.com/SFOE/ichtankestrom_Documentation/blob/main/Access%20Download%20the%20data.md)

## Disclaimer

This is a really "simple" script. There is no logging, no error handling, nothing like that. If you are willing to improve it, feel free, PRs are welcomed.
