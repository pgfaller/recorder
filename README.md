# Recorder

## Recorder setup

Install required modules via _pip_

```
pi@mercury:~/recorder $ sudo apt-get update
pi@mercury:~/recorder $ sudo apt-get install python-pip
pi@mercury:~/recorder $ sudo pip install Adafruit_DHT
```

- Create the files:
  -- recorder.py: The main python script that polls the DHT22 and stores results in SQLite3
  -- recorder.service: The systemd unit file to run the recorder
- Install and enable the service:

```
pi@mercury:~/recorder $ sudo cp recorder.service /etc/systemd/system/
pi@mercury:~/recorder $ systemctl start recorder
pi@mercury:~/recorder $ sudo systemctl enable recorder
```

## Web view setup

Follow the guide at https://dzone.com/articles/serving-flask-applications-with-uswgi-on-ubuntu

In the directory ~/recorder:

```
$ sudo pip install virtualenv
pi@mercury:~/recorder $ virtualenv venv
New python executable in /home/pi/recorder/venv/bin/python
Installing setuptools, pip, wheel...
done.
pi@mercury:~/recorder $ source venv/bin/activate
(venv) pi@mercury:~/recorder $ pip install flask uwsgi
DEPRECATION: Python 2.7 will reach the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 won't be maintained after that date. A future version of pip will drop support for Python 2.7.
Looking in indexes: https://pypi.org/simple, https://www.piwheels.org/simple
Collecting flask
...
Successfully built uwsgi MarkupSafe
Installing collected packages: click, Werkzeug, itsdangerous, MarkupSafe, Jinja2, flask, uwsgi
Successfully installed Jinja2-2.10.1 MarkupSafe-1.1.1 Werkzeug-0.15.2 click-7.0 flask-1.0.2 itsdangerous-1.1.0 uwsgi-2.0.18
(venv) pi@mercury:~/recorder $ vi app.py
(venv) pi@mercury:~/recorder $ python app.py
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:3000/ (Press CTRL+C to quit)
```

Test with:

```
peter@neptune:pgfaller.github.io$ curl http://mercury:3000
It Works!
192.168.0.165 - - [22/Apr/2019 15:11:44] "GET / HTTP/1.1" 200 -
(venv) pi@mercury:~/recorder $ vi wsgi.py
(venv) pi@mercury:~/recorder $ uwsgi --socket 0.0.0.0:3000 --protocol=http -w wsgi:app
*** Starting uWSGI 2.0.18 (32bit) on [Mon Apr 22 15:14:04 2019] ***
...
*** uWSGI is running in multiple interpreter mode ***
spawned uWSGI worker 1 (and the only) (pid: 4643, cores: 1)
```

Test with:

```peter@neptune:pgfaller.github.io$ curl http://mercury:3000
It Works!
[pid: 4643|app: 0|req: 1/1] 192.168.0.165 () {24 vars in 251 bytes} [Mon Apr 22 15:15:02 2019] GET / => generated 9 bytes in 6 msecs (HTTP/1.1 200) 2 headers in 78 bytes (1 switches on core 0)
(venv) pi@mercury:~/recorder $ vi recorder.ini
(venv) pi@mercury:~/recorder $ mv recorder{,-web}.ini
(venv) pi@mercury:~/recorder $ vi recorder-web.service
(venv) pi@mercury:~/recorder $ sudo cp recorder-web.service /etc/systemd/system/
(venv) pi@mercury:~/recorder $ sudo systemctl start recorder-web
(venv) pi@mercury:~/recorder $ sudo systemctl enable recorder-web
(venv) pi@mercury:~/recorder $ sudo vi /etc/nginx/sites-available/recorder-web
(venv) pi@mercury:~/recorder $ cp /etc/nginx/sites-available/recorder-web recorder-web.nginx
(venv) pi@mercury:~/recorder $ sudo ln -s /etc/nginx/sites-available/recorder-web /etc/nginx/sites-enabled/
(venv) pi@mercury:~/recorder $ ls -l /etc/nginx/sites-enabled/
total 0
lrwxrwxrwx 1 root root 34 Dec  5 16:41 default -> /etc/nginx/sites-available/default
lrwxrwxrwx 1 root root 39 Apr 22 15:38 recorder-web -> /etc/nginx/sites-available/recorder-web
(venv) pi@mercury:~/recorder $ sudo nginx -t
nginx: [warn] "ssl_stapling" ignored, issuer certificate not found
nginx: [warn] conflicting server name "192.168.0.25" on 0.0.0.0:80, ignored
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
(venv) pi@mercury:~/recorder $ sudo systemctl restart nginx
```

Test with:

```
peter@neptune:pgfaller.github.io$ curl http://mercury:8080
It Works!
```

Chart docs: https://www.chartjs.org/docs/latest/
