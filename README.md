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

cmd or powershell, `cd` to your `shared_mobility_updater` folder and

for the shared mobility part (https://github.com/SFOE/sharedmobility):

```
venv\Scripts\python shared_mobility.py

```

for the electric station part (https://github.com/SFOE/DIEMO-Documentation):

### Purpose

The `shared_mobility.py` script gets data from the swiss shared mobility provider.

The webservices are described here: https://sharedmobility.ch/gbfs.json
The 

The explanation can be found here: https://github.com/SFOE/sharedmobility

The `electric_mobility.py` script gets data out of https://data.geo.admin.ch/ch.bfe.ladestellen-elektromobilitaet/data/ch.bfe.ladestellen-elektromobilitaet_fr.json

### Disclaimer

This is a really "simple" script. There is no logging, no error handling,
nothing like that. If you are willing to improve it, feel free, PRs are
welcomed.
