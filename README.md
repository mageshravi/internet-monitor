# Internet monitor

Monitor your office/home's internet connectivity remotely.

## Setting up the logger (flask app)

Create a new virtual environment

```bash
# create new virtualenv "internet-monitor" using virtualenvwrapper
mkvirtualenv internet-monitor
```

Install the required python packages

```bash
pip install -r pip-requirements
```

Set up the database

```console
$ python3
>>> from imonitor_logger import db, Client, InternetStatus
>>> db.create_all()
>>> client = Client(name='office-desktop', api_key='random-string', api_secret='some-other-random-string')
>>> internet_status = InternetStatus(status='ONLINE')
>>> db.session.add(client)
>>> db.session.add(internet_status)
>>> db.session.commit()
>>> Client.query.first()
<Client office-desktop>
>>> InternetStatus.query.first()
<InternetStatus ONLINE>
>>> exit()
```

The flask app (in `imonitor_logger.py`) is deployed in a cloud hosted server. I recommend using [uWSGI on nginx](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04).

## Setting up the monitoring script

The monitoring script `imonitor.py` also resides in the cloud hosted server (alongside the `imonitor_logger.py`) and checks the logs in the database. If no new records are found within the last 120 seconds, then it triggers a notification to the configured telegram bot.

The monitoring script requires the following ENV variables to be defined.

```ini
BOT_TOKEN # the telegram bot token
BOT_CHATID # the telegram bot chat-id
DB_LOCATION # absolute path to imonitor.db
```

We'll use a wrapper shell script for this purpose. Create a new file `imonitor.sh` with the following contents

```bash
#!/usr/bin/env bash

export BOT_TOKEN=telegram-bot-token
export BOT_CHATID=telegram-bot-chatid
export DB_LOCATION=/absolute/path/to/imonitor.db

/absolute/path/to/virtualenv/bin/python3 /absolute/path/to/imonitor.py
```

Setup a cron job

```bash
crontab -e
```

Add the following line to the end,

```
*/120 * * * * /absolute/path/to/imonitor.sh >> /absolute/path/to/imonitor_cron.log 2>&1
```

## Setting up the client

Update the client.sh with the api_key and api_secret generated in the previous steps. Setup a cron job to run this script every 2 minutes.

In your terminal, type

```bash
crontab -e
```

Then add the following line at the end

```
*/2 * * * * /bin/bash /path/to/your/client.sh
```
