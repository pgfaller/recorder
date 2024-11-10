#!/usr/bin/python
#
# Copied from SQLite3 and Adafruit examples ...
#

import sqlite3
from sqlite3 import Error
import sys
import os
import Adafruit_DHT
import time
import signal
import requests
import socket
#from prometheus_client import start_http_server, Gauge


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        print('Connected to the database')
        return conn
    except Error as e:
        print('Unable to connect', e)

    return None


def create_temp_humidity_table(cursor):
    """ Create the table to hold temperature and humidity readings
    :param cursor: database cursor
    """
    table_def = """ CREATE TABLE IF NOT EXISTS temperature_humidity (
        timestamp integer PRIMARY KEY,
        hostname string(64),
        temperature numeric,
        humidity numeric
    ); """
    try:
        cursor.execute(table_def)
        print('Table created')
    except Error as e:
        print('Unable to create table', e)


def store_temp_humidity(cursor, now, temperature, humidity):
    """ Store a single temperature and humidity reading
    :param cursor: SQLite3 cursor
    :param now: timestamp
    :param temperature: temperature reading
    :param humidity: humidity reading
    :return: ID of last insert
    """
    sql_text = """ INSERT INTO temperature_humidity (hostname, timestamp, temperature, humidity)
                   VALUES(?,?,?,?) """
    try:
        cursor.execute(sql_text, (socket.gethostname(), now, temperature, humidity))
        print('Record inserted', cursor.lastrowid)
        return cursor.lastrowid
    except Error as e:
        print(e)


def send_recording(url, now, temperature, humidity):
    try:
        recording = {}
        recording['hostname'] = socket.gethostname()
        recording['timestamp'] = now
        recording['temperature'] = temperature
        recording['humidity'] = humidity
        r = requests.post(url, json=recording)
        print(r.status_code, r.reason)
    except Error as e:
        print(e)


def signal_handler(sig, frame):
    print('Exiting on signal', sig)
    conn.close
    sys.exit(0)


if __name__ == '__main__':
    try:
        # Parse command line parameters.
        sensor_args = {'11': Adafruit_DHT.DHT11,
                       '22': Adafruit_DHT.DHT22,
                       '2302': Adafruit_DHT.AM2302}
        if len(sys.argv) == 4 and sys.argv[1] in sensor_args:
            sensor = sensor_args[sys.argv[1]]
            pin = sys.argv[2]
            interval = int(sys.argv[3])
        else:
            print(
                'Usage: sudo ./recorder.py [11|22|2302] <GPIO pin number> <interval>')
            print(
                'Example: sudo ./recorder.py 22 18 15 - Read from an DHT22 connected to GPIO pin #4')
            sys.exit(1)

        # Connect to the database
        conn = create_connection("recordings.db")
        cursor = conn.cursor()
        create_temp_humidity_table(cursor)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Get the Azure URL
        try:
            url = os.environ['AZ_URL']
        except KeyError as ke:
            print('No AZ_URL found')
            url = None

#        # Define Prometheus metrics
#        temperature_gauge = Gauge('environment_temperature', 'Measured temperature');
#        humidity_gauge = Gauge('environment_humidity', 'Measured humidity');
#        start_http_server(8000);
        
        # Periodic readings
        while(True):
            # Try to grab a sensor reading.  Use the read_retry method which will retry up
            # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
            print('Reading sensors')
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

            # Note that sometimes you won't get a reading and
            # the results will be null (because Linux can't
            # guarantee the timing of calls to read the sensor).
            # If this happens try again!
            if humidity is not None and temperature is not None:
                now = time.time()
                print(
                    'Time={2:0.1f} Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity, now))
                store_temp_humidity(cursor, int(now), temperature, humidity)
                conn.commit()
                if url is not None:
                    send_recording(url, int(now), temperature, humidity)
#                temperature_gauge.set(temperature);
#                humidity_gauge.set(humidity);
            else:
                print('Failed to get reading. Try again!')
            time.sleep(interval)

    except Error as e:
        print(e)
        exit(1)
    finally:
        conn.close()
