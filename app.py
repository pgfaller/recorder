import sqlite3
from sqlite3 import Error
from flask import (
    Flask,
    g,
    jsonify,
    request,
    render_template
)
import json
import socket
import io
import base64
import pandas as pd
from matplotlib.figure import Figure     
from matplotlib import pyplot as plt                 

app = Flask(__name__, static_url_path='')

DATABASE = 'recordings.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def get_data(hostname, limit):
    """ Retrieve readings from SQLite database """
    sql_text = """ SELECT hostname, timestamp, temperature, humidity
        FROM temperature_humidity
        WHERE hostname=?
        ORDER BY timestamp DESC LIMIT(?)
    """
    db = get_db()
    data = db.execute(sql_text, (hostname, str(limit),)).fetchall()
    return data


def put_data(hostname, timestamp, temperature, humidity):
    """ Insert a reading into the SQLite database """
    sql_text = """ INSERT INTO temperature_humidity (hostname, timestamp, temperature, humidity)
        VALUES(?, ?, ?, ?) 
    """
    db = get_db()
    cur = db.cursor()
    cur.execute(sql_text, (hostname, timestamp, temperature, humidity,))
    db.commit()
    return cur.lastrowid

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
def root():
    return app.send_static_file('index.html')


@app.route("/data")
def data():
    limit = request.args.get('limit', default = 50, type = int)
    hostname = request.args.get('hostname', default = socket.gethostname(), type = str)
    data = get_data(hostname, limit)
    return json.dumps([tuple(row) for row in data])


@app.route("/chart")
def chart():
    limit = request.args.get('limit', default = 50, type = int)
    hostname = request.args.get('hostname', default = socket.gethostname(), type = str)
    data = get_data(hostname, limit)

    db = get_db()
    query_template = """
        SELECT timestamp, temperature, humidity
        FROM temperature_humidity
        WHERE hostname='{}'
        ORDER BY timestamp DESC LIMIT({})
        """
    query = query_template.format(hostname, limit)
    recordings = pd.read_sql_query(query, db)
    recordings['timestamp'] = pd.to_datetime(recordings['timestamp'],unit='s')
    plot_df = recordings.set_index('timestamp')

    fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True)
    plt.subplots_adjust(wspace=1.0, hspace=0.5)

    plot_df['temperature'].plot(ax=axes[0], style='c-')
    axes[0].set_title('Temperature')
    axes[0].grid(b=True, which='major', color='#666666', linestyle='-')
    axes[0].grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

    plot_df['humidity'].plot(ax=axes[1], style='g-')
    axes[1].set_title('Humidity')
    axes[1].grid(b=True, which='major', color='#666666', linestyle='-')
    axes[1].grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    buffer = b''.join(buf)
    b2 = base64.b64encode(buffer)
    plot_data=b2.decode('utf-8')

    return render_template('chart.html', recordings=data, plot_data=plot_data)


@app.route("/insert", methods=['POST'])
def insert():
    record = request.get_json(force=True)
    hostname = record['hostname']
    timestamp = record['timestamp']
    temperature = record['temperature']
    humidity = record['humidity']
    rowid = put_data(hostname, timestamp, temperature, humidity)
    record['rowid'] = rowid
    return json.dumps(record)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
