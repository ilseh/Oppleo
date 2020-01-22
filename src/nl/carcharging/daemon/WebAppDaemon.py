# Intended to become the WebApp as service launcher
import logging
from flask import Flask
from flask_socketio import SocketIO


# app initiliazation
app = Flask(__name__)
socketio = SocketIO(app)

"""
  WSGI - Web Server Gateway Interface
  PEP 333 at http://www.python.org/dev/peps/pep-0333/
  The uWSGI Project https://uwsgi-docs.readthedocs.io/en/latest/
"""
def application(environ, start_response):
    status = '200 OK'
    output = 'Hello World!'

    response_headers = [('Content-type', 'text/plain'),
                    ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]



@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"
    
if __name__ == "__main__":

    logger = logging.getLogger('nl.carcharging.daemon.WebAppDaemon')
    logger.debug('Initializing WebAppDaemon')

    app.run(host='0.0.0.0')

    cnt = 0

    while True:
        socketio.sleep(5)
        logger.debug('tick {}'.format(cnt))
