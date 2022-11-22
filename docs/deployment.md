# Deployment instructions

This document contains 3 instructions:

1. [to deploy locally on a linux PC](#part-1-instructions-for-deploying-the-project-locally-on-linux)
2. [to deploy on a linux server](#part-2-instructions-for-deploying-the-project-on-a-linux-server)
3. [to deploy using Dokku on a linux server](#part-3-instructions-for-deploying-the-project-on-a-linux-server-with-dokku)

## Part 1: Instructions for deploying the project locally on Linux

### Set up the environment

Firstly make sure Git is installed, then:

1. Clone the project

    ```
    $ git clone https://github.com/StreetScienceCommunity/DNAnalyzer.git
    ```

2. Move into the project folder

    ```
    $ cd /path/to/the/project
    ```

3. Set up the project environment

    - With conda

        1. Install [miniconda](https://docs.conda.io/en/latest/miniconda.html)
        2. Create conda environment

            ```
            $ conda env create -f environment.yml
            ```

        3. Activate conda environment

            ```
            $ conda activate dnanalyzer
            ```

    - Without conda on Ubuntu

        1. Make sure Python is installed
        2. Install PostgreSQL (version 11 or 14)

            ```
            $ sudo apt install postgresql postgresql-contrib -y
            ```

        3. Install the project's dependencies:

            ```
            $ pip3 install -r requirements.txt
            ```

            If errors occurred for building wheel for Pillow, then the following commands would be needed:

            ```
            $ apt-get install libjpeg-dev zlib1g-dev
            # if not working after this, also try
            $ sudo pip install -U setuptools
            ```

### Setting up the database

1. Create database

    Within conda environment:

    1. Create a base database locally

        ```
        $ initdb -D dnanalyzer
        ```

    2. Start the server modus/instance of postgres

        ```
        $ pg_ctl -D dnanalyzer -l logfile start
        ```

    3. Create a non-superuser (more safety!)

        ```
        $ createuser --encrypted --pwprompt <mynonsuperuser>
        ```

    4. Create inner database inside the base database

        ```
        $ createdb --owner=<mynonsuperuser> dnanalyzer
        ```


    Without conda

    ```
    $ sudo -u postgres psql
        create database dnanalyzer;
        create user {usernameYouWant} with encrypted password '{yourPassword}';
        grant all privileges on database dnanalyzer to {usernameYouWant};
        exit
    ```

2. Configure the database details for the project:
    1. Copy the `db_config.py.in` to `db_config.py`
    2. Edit `db_config.py` to change username, password according the previous setup

### Launch the project

```
$ python app.py
```

## Part 2: Instructions for deploying the project on a Linux server

### Firstly you should have access to the server using tools like ssh

### Setting up the environment
update the system applications
```
    sudo apt update -y
    sudo apt upgrade -y
```

install necessary tools
```
    sudo apt-get install git nginx -y
    sudo apt install postgresql postgresql-contrib -y
    sudo apt install python3-pip -y
    sudo apt-get install python3-venv -y
```

clone the project
```
    git clone https://github.com/StreetScienceCommunity/DNAnalyzer.git
```

install conda
```
    mkdir -p ~/miniconda3
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
    bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    rm -rf ~/miniconda3/miniconda.sh
    ~/miniconda3/bin/conda init bash
    ~/miniconda3/bin/conda init zsh
```
### Setting up the database
```
    sudo -u postgres psql
    create database {nameOfTheDatabaseYouWant};
    create user {usernameYouWant} with encrypted password '{yourPassword}';
    grant all privileges on database {nameOfTheDatabaseYouWant} to {usernameYouWant};
    exit
    sudo vi /etc/postgresql/{Your postgres version}/main/pg_hba.conf
    # and change postgres and local to use password(md5 in the case) (2 or 3 changes should be made)
    sudo systemctl restart postgresql
```

### Setting up the project environment
```
    cd /path/to/the/project
    conda activate myenv
    pip3 install -r requirements.txt
    cp db_config.py.in db_config.py
    vi db_config.py # edit the config file to change database, username, password according your own
```

>   if errors occurred for building wheel for Pillow, then the following commands would be needed:
>   ```
>   apt-get install libjpeg-dev zlib1g-dev
>   # if not working after this, also try
>   sudo pip install -U setuptools
>   ```

now the project should be ready to run locally
```
    python app.py
```

### Next steps are for deploying the project with gunicorn and nginx
```
    pip3 install gunicorn
    vi {project root}/wsgi.py
    gunicorn --bind 0.0.0.0:5000 wsgi:app
```

If everything is fine, you should get the following output:
```
    Starting gunicorn 20.1.0
    Listening at: http://0.0.0.0:5000 (9352)
    Using worker: sync
    Booting worker with pid: 9354"
```




### Create a Systemd Service File for Flask Application
```
    vi /etc/systemd/system/flask.service
```
Add the following lines:
```
    [Unit]
    Description=Gunicorn instance to serve Flask
    After=network.target
    [Service]
    User=root
    Group=www-data
    WorkingDirectory=/root/project
    Environment="PATH=/root/project/venv/bin"
    ExecStart=/root/project/venv/bin/gunicorn --bind 0.0.0.0:5000 wsgi:app
    [Install]
    WantedBy=multi-user.target
```
Save and close the file then set proper ownership and permission to flask project:

```
    chown -R root:www-data /root/project
    chmod -R 775 /root/project
```
Next, reload the systemd daemon with the following command:
```
    systemctl daemon-reload
```
Next, start the flask service and enable it to start at system reboot:

```
    systemctl start flask
    systemctl enable flask
```
Next, verify the status of the flask with the following command:

```
    systemctl status flask
```

### Configure Nginx as a Reverse Proxy for Flask Application

Next, you will need to configure Nginx as a reverse proxy to serve the Flask application through port 80. To do so, create an Nginx virtual host configuration file:
```
    nano /etc/nginx/conf.d/flask.conf
```

Add the following lines:
```
    server {
        listen 80;
        server_name flask.example.com;
        location / {
            include proxy_params;
            proxy_pass  http://127.0.0.1:5000;
        }
    }
```

Save and close the file then verify the Nginx for any syntax error:
```
    nginx -t
```
You should see the following output:
```
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful
```
Finally, restart the Nginx service to apply the changes:

```
    systemctl restart nginx
```
At this point, your Flask application is installed, configured, and hosted with an Nginx proxy. You can now access it using your domain http://flask.example.com.



## Part 3: Instructions for deploying the project on a Linux server with Dokku

### Server requirment

To start using Dokku, you'll need a system that meets the following minimum requirements:
A fresh installation of any of the following operating systems:
1. Ubuntu 18.04/20.04/22.04
2. Debian 10+ x64

To avoid memory pressure during builds or runtime of the project applications, system memory should be at least 1 GB.

### Install dokku and setup SSH key

the instructions for installing dukku and setuping ssh key can be found on the official [Dokku Documentation](https://dokku.com/docs/getting-started/installation/).


### Setup Dokku apps and services

Get the project on the your pc and also on the server


```
git clone https://github.com/StreetScienceCommunity/DNAnalyzer.git
```

Create the app
```
# on the Dokku host
dokku apps:create dnanalyzer
```

Install the Dokku Postgres plugin
```
# on the Dokku host
# install the postgres plugin
# plugin installation requires root, hence the user change
sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git

# create a postgres service with the name dnanalyzer
dokku postgres:create dnanalyzer
```

Linking the Postgres service to the app
```
# on the Dokku host
# each official datastore offers a `link` method to link a service to any application
dokku postgres:link dnanalyzer dnanalyzer
```

Get the host and port infos of the database using
```
# on the Dokku host
dokku postgres:info dnanalyzer
```

In the DNS field, you can get the host and port infos.

### Setting up the database details in the project
```
# from your local machine
cd DNAnalyzer
cp db_config.py.in db_config.py
# edit the config file to change database, username, password according your own
vi db_config.py
# forcely add and commit the config file to the git
git add --force db_config.py
git commit -m "add db_config"
```

### Deploy the project

This part use ```dokku.me``` as the ip address of the server, remember to substitute it with the real ip address of your server.

```
# from your local machine
# the remote username *must* be dokku or pushes will fail
git remote add dokku dokku@dokku.me:dnanalyzer
git push dokku main:master
```

Once the deployment is finished, you should have output indicting that ```Application deployed```.
