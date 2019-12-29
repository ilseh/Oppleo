# RestfulCharging


## Developer specific
sudo apt-get install libpq-dev
sudo apt install python3.6-dev
sudo apt-get install build-essential

install docker and docker-compose
install liquibase

(You need Java for liquibase.)

Check the liquibase.properties and the docker-compose.yml to make sure it matches your situation.
Set the DATABASE_URL AND CARCHARGING_ENV environment properties of the run script.
For example (assuming docker is running in a virtual machine):
DATABASE_URL=postgresql://car:charging123@192.168.99.100:5432/carcharging
CARCHARGING_ENV=development

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
   $ pip3 -r requirements.txt
   ```
5. Update the DATABASE_URL and CARCHARGING_ENV values in the start.sh to match your situation 