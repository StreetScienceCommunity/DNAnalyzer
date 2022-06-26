# Dnapi

This document is about the Server Side of Dnanalyzer. It contains descriptions about the API and the Website.


## Flask Backend

### Requirements

The API relies on Flask and Postgres infrastructure, it is advised to run the API in a virtual environment.

The additional packages are:

* wheel
* Pillow
* Flask
* Flask-Login
* flask-marshmallow
* Flask-SQLAlchemy
* marshmallow
* marshmallow-sqlalchemy
* psycopg2

More information about requirements file and installation script can be found in the installation instructions below.

### Installation

```bash
$ cd dnapi
```

Set up and activate Python `virtualenv`

```bash
$ python3 -m venv ./myvenv
$ source myvenv/bin/activate
```

Install the required modules.

```bash
$ pip3 install -r requirements.txt
```

Next, create a `db_config.py` file:

```bash
$ cp db_config.py.in db_config.py
```

Change the database parameters to suit yours, make sure the database exists and the user has the privilage.