from datetime import datetime
import re

from flask import Flask, abort, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///imonitor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Client(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    api_key = db.Column(db.String(32), unique=True, nullable=False)
    api_secret = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Client %s>' % self.name


class RequestLog(db.Model):
    id = db.Column('request_log_id', db.Integer, primary_key=True)
    logged_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = db.relationship('Client', backref=db.backref('client', lazy=True))

    def __repr__(self):
        return '<RequestLog %s>' % self.logged_at


class InternetStatus(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    status = db.Column(db.String(16), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<InternetStatus %s>' % self.status


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        api_key = request.json['api_key']
        api_secret = request.json['api_secret']
        client = validate_client(api_key, api_secret)

        if not client:
            print('Invalid credentials => api_key: %s ; api_secret: %s' % (api_key, api_secret))
            abort(401)
        # endif

        # log request
        log = RequestLog(client=client)
        db.session.add(log)
        db.session.commit()

        return 'Success'
    else:
        return 'Internet monitor up and running'


def validate_client(api_key, api_secret):
    """validate the api_key, api_secret
    returns Client or None
    """
    md5_pattern = re.compile('^[A-Za-z0-9]+$')

    if not md5_pattern.match(api_key):
        print('Invalid api_key %s' % api_key)
        return False
    # endif

    if not md5_pattern.match(api_secret):
        print('Invalid api_secret %s' % api_secret)
        return False
    # endif

    return Client.query.filter_by(api_key=api_key, api_secret=api_secret).first()
