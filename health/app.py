from time import strftime
import uuid
import connexion
from connexion import NoContent
import datetime
import requests
import json
import yaml
import logging, logging.config
from flask_cors import CORS, cross_origin
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from health import Health


if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

DB_ENGINE = create_engine(f"sqlite:///{app_config['datastore']['filename']}")

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def create_table():
    """create the table if it doesn't exist"""
    conn = sqlite3.connect(app_config['datastore']['filename'])
    c = conn.cursor()
    c.execute('''
        CREATE TABLE if not exists health
        (id INTEGER PRIMARY KEY ASC, 
        receiver VARCHAR(10) NOT NULL,
        storage VARCHAR(10) NOT NULL,
        processing VARCHAR(10),
        audit VARCHAR(10),
        last_updated VARCHAR(100) NOT NULL)
        ''')

    conn.commit()
    conn.close()

def get_stats():
    """get the stats from storage application"""
    session = DB_SESSION()
    time = datetime.datetime.now()
    readings = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    
    if readings == None:
        ss = Stats(5,6,100, 200, 10,10, time)
        session.add(ss)
        session.commit()
        session.close()
        return None

    else:
        result = readings.to_dict()
        session.close()    
        return result, 201


def populate_db():
    """ store the result in sqlite """



def init_scheduler():
    """ initialize the scheduler to run periodically"""
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_db,
                'interval',
                seconds=app_config['scheduler']['period_sec']
                )
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir="")
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)