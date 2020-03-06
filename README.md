# RestfulCharging


## Developer specific
sudo apt-get install libpq-dev
sudo apt install python3.6-dev
sudo apt-get install build-essential

install docker and docker-compose
install liquibase

(You need Java for liquibase.)

Check the liquibase.properties and the docker-compose.yml to make sure it matches your situation.
Set the DATABASE_URL AND oppleo_ENV environment properties of the run script.
For example (assuming docker is running in a virtual machine):
DATABASE_URL=postgresql://username:password@192.168.99.100:5432/charger
oppleo_ENV=development

execute docker-compose up to run your developement postgres db. On my windows it is in a virtual machine, hence the ip, on linux it is on localhost.

## Database schema setup
In db folder, update the liquibase.properties to match your situation, then run:
``` shell script
$ liquibase update
```

## Setup to run the service
1. Clone this repo on the machine you want to run it.
2. Changedir to the main folder of the repo (/somedir/RestfulCharging/).
3. Make a virtual env: 
    ```shell script
    $ python3 -m venv venv
    ```
4. Install the python libs in the venv   
   ```shell script
   $ source venv/bin/activate
   $ pip3 install -r requirements.txt
   ```
5. Update the DATABASE_URL and oppleo_ENV values in the start.sh to match your situation 

### Let is start a boot time
In /etc/init.d/ add a file (ie measure_energy_devices.sh) and put in content:
```shell script
# /etc/init.d/measure_energy_devices.sh
### BEGIN INIT INFO
# Provides:          measure_energy_devices.sh
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start measure_energy_device at boot time
# Description:       Enable measure_energy_devices at boot time to write energy measures to postgres db
### END INIT INFO
```

## Operational info
The log is in  `/tmp/measure_electricity_usage.log` and the pid of the daemon in `/tmp/measure_electricity_usage.pid`
Locations are currently hardcoded in `MeasureElectricityUsage.py`
Loglevel (hardcoded) put on debug.