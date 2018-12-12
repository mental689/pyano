PyANO 2
============

## Introduction
This is the official repository of the automated annotation tool PyANO 2.
With this project, we aim on providing a tool to reduce the cost of building new datasets for computer vision tasks.
The following three activities will be modeled in this project:

* __Collecting videos from video sharing services such as YouTube__: Searching based on text keywords. We rely on external search services such as YouTube.

* __Survey and report tools__: this module provides user tools to ask participants questions in controlled and well-designed experiments. One popular use cases of these tools is to filter further irrelevant videos by asking participants questions.

* __Spatio-temporal annotation tools__: We rely on the popular annotation tool VATIC for this purpose. Annotators will be asked to annotate video frames in with bounding boxes.


## Installation

#### Requirements

* Python 3.6+
* pip 9.0+
* MySQL 5.7+

To install the remaining requirements:

```bash
$ pip install -r requirements.txt
$ source env.sh # please modify this if you want to install mysql-server in Ubuntu.
```

Finally, you have to install [pyvision](https://github.com/cvondrick/pyvision) package of Carl Vondrick to have spatio-temporal functions to work.

## Basic usage

### Update migrations

In folder `pyano2/migrations/`, we leave sample migrations file to migrate the Django's database structure into a MySQL database.

If you have any troubles, please remove all generated migrations in `pyano2/migrations/` and generate again by 

```bash
$ mysql # if you need to run as root: mysql -uroot -p
mysql > CREATE DATABASE pyano2 CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
mysql > exit
## Please modify your settings in pyano/settings.py to match your MySQL server settings.
$ python3 manage.py makemigrations # to generate the migration files
$ python3 manage.py migrate # to migrate your databases to pyano2 that we have created.
```

### Detailed documentation

Please see [DOCUMENTATION](./DOCUMENTATION.md). But we don't explain again what are alreday in [Django's documentation](https://docs.djangoproject.com/en/2.1/) such as createing a superuser, where to access admin's page, etc.

## Demo

* Demo site: [http://13.58.121.50:8000](http://13.58.121.50:8000)

* You need to [create an account](http://13.58.121.50:8000/register/) to use the demo.