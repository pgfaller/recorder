import sqlite3
from sqlite3 import Error
from flask import (
    Flask,
    g,
    jsonify
)
import json

app = Flask(__name__)

DATABASE = 'recordings.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
def hello():
    """ Retrieve readings from SQLite database """
    sql_text = """ SELECT timestamp, temperature, humidity
        FROM temperature_humidity order by timestamp desc limit(20)
    """
    db = get_db()
    data = db.execute(sql_text, ()).fetchall()
    return json.dumps([tuple(row) for row in data])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
