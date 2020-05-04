# Oppleo

Read the Wiki page for a description of Oppleo. You'll need a Raspberry Pi and a SmartEVSE based car charger setup.


## Install Oppleo on a Raspberry Pi 4

#### Prereqs
  * I run Oppleo on a Raspberry Pi 4. I have not tested other versions, I can only assume a 3 would work too. If you need to order one, get a 4, if you have one laying around give it a try.
  * You'll need a SmartEVSE to control charging. Oppleo pulls a pin down, so any other EVSE with a similar control pin might work.
  * Make sure apt-get is up to date  
    > `sudo apt-get update && sudo apt-get upgrade`
  * RFID reader, LED, buzzer, RTC. Technically not needed, but makes for better experience.
  * A Raspberry does not come with a Real-Time Clock (RTC). [Read up](https://thepihut.com/blogs/raspberry-pi-tutorials/17209332-adding-a-real-time-clock-to-your-raspberry-pi) to understand if you want one.
    * Install [RasClock](https://afterthoughtsoftware.com/products/rasclock) (Real Time Clock)
    * Check it it is installed using `sudo hwclock -r`
    * Start after boot `sudo nano /boot/config.txt` add
      > `# RasClock RealTime Clock`  
      > `dtoverlay=i2c-rtc,pcf2127`
      * Reboot your Raspberry
      > `sudo reboot`
  * `ssh` enabled on the Raspberry. 
    * Add an empty file named `ssh` (no extension) to the root of the sdcard to enable ssh after boot on the Raspberry. You'll probably need ssh to install Python and Postgress anyway.
  * Pyhton3 and pip installed
    > `sudo apt-get install python3-dev python3-pip`
  * Postgres (Google for [How-to](https://opensource.com/article/17/10/set-postgres-database-your-raspberry-pi)'s) with a database, a user with rights to that database, and a password.
  * Install SPIdev, a python module for interfacing with SPI devices. This is required to interface with the RFID reader which uses the SPI bus.
    > `sudo pip3 install spidev`  
    * Enable SPI and the PCM at boot. Edit /boot/config.txt
	  > `sudo nano /boot/config.txt`
    * Add these lines
      > `dtparam=spi=on` 
      > `dtoverlay=spi-bcm2708`
      
      	lsmod | grep spi
spidev                 20480  0
spi_bcm2835            20480  0
      
      
  * Install mfrc522, the interface module for the RFID reader.
	> `sudo pip3 install mfrc522`
  * Install RPi.GPIO, a PyPi python module for interfacing with the Raspberry Gneral Purpose IO (GPPIO) pins. This is required to interface with the RTC, LED, the Buzzer, and the SmartEVSE.
    > `sudo pip install RPi.GPIO`
  * git installed on your Raspberry
    > `sudo apt-get install git`
  
  
 #### Installation
 Oppleo is not a nicely packaged resource. Basically you'll pull the developer code and run that. 
 Use ssh to login to the Raspberry. You'' end up in `/home/pi`
 
 * Create a folder named __Oppleo__ in the pi home directory
 > `mkdir oppleo`
 > `cd oppleo`
 
 * Initialise the folder as git repo
 
 
 Install 
  



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
