
# Run main on MacBook Home
env PYTHONPATH=src:./src:/Library/Frameworks/Python.framework/Versions/3.7/bin /Users/frans/Projects/RestfulCharging/venv/bin/python ./src/nl/carcharging/webapp/WebApp.py

# Old cmd to run uWSGI
uwsgi --ini /home/pi/development/RestfulCharging/webapp/CarChargerWebApp.ini --logger file:/tmp/uwsgi.log -H /home/pi/development/RestfulCharging/venv/
