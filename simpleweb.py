import sqlite3
from sqlite3 import Error
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from urllib.parse import parse_qs
import json
import socket
import traceback

def get_data(hostname, limit):
    """ Retrieve readings from SQLite database """
    sql_text = """ SELECT hostname, timestamp, temperature, humidity
        FROM temperature_humidity
        WHERE hostname=?
        ORDER BY timestamp DESC LIMIT(?)
    """
    data = db.execute(sql_text, (hostname, str(limit),)).fetchall()
    return data
def put_data(hostname, timestamp, temperature, humidity):
    """ Insert a reading into the SQLite database """
    sql_text = """ INSERT INTO temperature_humidity (hostname, timestamp, temperature, humidity)
        VALUES(?, ?, ?, ?) 
    """
    cur = db.cursor()
    cur.execute(sql_text, (hostname, timestamp, temperature, humidity,))
    db.commit()
    return cur.lastrowid

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print(self.path)
        parsed = urlparse(self.path)
        print(parsed)
        queries = parse_qs(parsed.query)
        print(queries)
        try:
            limit = queries['limit'][-1]
        except KeyError:
            limit = 50
        print(limit)
        try:
            hostname = queries['hostname'][-1]
        except KeyError:
            hostname = socket.gethostname()
        print(hostname)
        try:
            data = get_data(hostname, limit)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps([tuple(row) for row in data]), 'utf-8'))
        except:
            errinfo = traceback.format_exc()
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(errinfo, 'utf-8'))

serverPort = 8000
DATABASE = 'recordings.db'

if __name__ == "__main__":
    global db
    db = sqlite3.connect(DATABASE)
    httpd = HTTPServer(('', serverPort), SimpleHTTPRequestHandler)
    print("Server started http://%s:%s" % (socket.gethostname(), serverPort))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if db is not None:
    db.close()
httpd.server_close()
print("Server stopped.")
