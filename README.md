# shared mobility updater

### Requirements

Python 3.6+

### Install

* Get the code and create the virtual environment:

```
git clone https://github.com/sitn/shared_mobility_updater.git
cd shared_mobility_updater
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

* Copy-paste the `config.yml.sample` file
* Rename it to `config.yml`
* Use the `create_table.sql`, adapt the table name and schema if necessary

That's it

### Run it

cmd or powershell, `cd` to your `shared_mobility_updater` folder and:


```
venv\Scripts\python shared_mobility.py

```

### Purpose

This script get data from the swiss shared mobility provider.

The webservices are described here: https://sharedmobility.ch/gbfs.json
The 

The explanation can be found here: https://github.com/SFOE/sharedmobility

### Disclaimer

This is a really "simple" script. There is no logging, no error handling,
nothing like that. If you are willing to improve it, feel free, PRs are
welcomed.
