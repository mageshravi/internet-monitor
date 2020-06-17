import sqlite3

from dateutil import tz
from dateutil.parser import parse
from dateutil.utils import datetime
from urllib.parse import quote
import requests
import os


from_zone = tz.gettz('UTC')
to_zone = tz.gettz('Asia/Kolkata')
watch_interval = 120


def set_status_to_offline(conn: sqlite3.Connection):
    c = conn.cursor()
    c.execute('INSERT INTO internet_status (status, created_at) VALUES ("OFFLINE", "%s")' % str(datetime.utcnow()))
    conn.commit()


def set_status_to_online(conn: sqlite3.Connection):
    c = conn.cursor()
    c.execute('INSERT INTO internet_status (status, created_at) VALUES ("ONLINE", "%s")' % str(datetime.utcnow()))
    conn.commit()


def get_status(cursor: sqlite3.Connection.cursor):
    resultset = cursor.execute('SELECT * FROM internet_status ORDER BY id DESC LIMIT 1')
    status_id, status, created_at = resultset.fetchone()
    return (status, created_at)


def parse_to_local_timezone(dtstr: str):
    dt = parse(dtstr)                   # parse string
    dt = dt.replace(tzinfo=from_zone)   # make timezone aware
    return dt.astimezone(to_zone)       # convert to local timezone

def send_telegram_notification(message):
    bot_token = os.getenv('BOT_TOKEN')
    bot_chatID = os.getenv('BOT_CHATID')
    send_text = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&parse_mode=MarkdownV2&text=%s' % (
        bot_token, bot_chatID, quote(message))
    response = requests.get(send_text)
    print(response.json())


if __name__ == '__main__':
    conn = sqlite3.connect(os.getenv('DB_LOCATION', 'imonitor.db'))
    c = conn.cursor()

    resultset = c.execute('SELECT * FROM request_log ORDER BY logged_at DESC LIMIT 1')
    log_id, logged_at, client_id = resultset.fetchone()

    logged_dt = parse_to_local_timezone(logged_at)

    internet_status, internet_status_ts = get_status(c)
    print("INTERNET STATUS: %s" % internet_status)
    if internet_status == 'ONLINE':
        if (datetime.now(tz=to_zone) - logged_dt).seconds > watch_interval:
            message = ('🔴 *Internet is DOWN*\n\n'
                    '_Last known connection on_\n%s' % logged_dt.strftime('%d %b %Y at %I:%M %p'))
            send_telegram_notification(message)
            set_status_to_offline(conn)
            exit()
        # endif
    elif internet_status == 'OFFLINE':
        now = datetime.now(tz=to_zone)
        if (now - logged_dt).seconds < watch_interval:
            internet_status_dt = parse_to_local_timezone(internet_status_ts)
            downtime = now - internet_status_dt
            message = ('🟢 *Internet is UP*\n\n'
                       '_Last known connection on_\n%s\n\n'
                       '_Approximate downtime_\n%dmins' % (
                           logged_dt.strftime('%d %b %Y at %I:%M %p'),
                           int(downtime.seconds/60)
                        ))
            send_telegram_notification(message)
            set_status_to_online(conn)
    # endif

    conn.commit()
    conn.close()
