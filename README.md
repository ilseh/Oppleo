# RestfulCharging


## Developer
sudo apt-get install libpq-dev
sudo apt install python3.6-dev
sudo apt-get install build-essential

install docker and docker-compose
install liquibase

(You need Java for liquibase. If not installed, i suggest install via sdkman (which needs zip).)

Check the liquibase.properties and the docker-compose.yml to make sure it matches your situation.
Set the DATABASE_URL AND CARCHARGING_ENV environment properties of the run script.
Ie in Intellij, make a run config for your run.py. In the environment of the run config set (assuming on windows with docker-terminal):
DATABASE_URL=postgresql://car:charging123@192.168.99.100:5432/carcharging
CARCHARGING_ENV=development

execute docker-compose up to run your developement postgres db. On my windows it is in a virtual machine, hence the ip, on linux it is on localhost.

## Database
In db folder, run `liquibase update`.
