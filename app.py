import sqlite3
from sqlite3 import Error
from flask import (
    Flask,
    g,
    jsonify,
    render_template
)
import json

app = Flask(__name__, static_url_path='')

DATABASE = 'recordings.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def get_data(limit):
    """ Retrieve readings from SQLite database """
    sql_text = """ SELECT timestamp, temperature, humidity
        FROM temperature_humidity order by timestamp desc limit(?)
    """
    db = get_db()
    data = db.execute(sql_text, (str(limit),)).fetchall()
    return data


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
def root():
    return app.send_static_file('index.html')


@app.route("/data")
@app.route("/data/<int:limit>")
def data(limit=50):
    data = get_data(limit)
    return json.dumps([tuple(row) for row in data])


@app.route("/chart")
@app.route("/chart/<int:limit>")
def chart(limit=50):
    data = get_data(limit)
    return render_template('chart.html', recordings=data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
