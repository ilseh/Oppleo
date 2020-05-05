# Oppleo

The Oppleo software package aims to provide additional functionality to extend a basic SmartEVSE based car charger adding RFID tags, a buzzer and LED, an online web front with basic authentication, kWh meter loggin to a database, off-peak charging, and Excel and PDF charge reports.

Combined with some additional components like a relais, cabling and proper connections, a SmartEVSE can be used to charge an electric vehicle from your one or three phase mains. It can do so while balancing the total power consumption. SmartEVSE allows control through a switch, which is used by Oppleo to control access and off peak charging. SmartEVSE also reports charge status through a PWM pin, which is read by Oppleo to provide LED and online charge status.

Oppleo uses modbus interfacing to connect with a kWh meter logging readings to a database. Oppleo can use Prowl to send push messages to the owner.

Oppleo is build using Python3/Flask and runs on a Raspberry Pi (4). You'll need a Raspberry Pi and a SmartEVSE based car charger setup.


## Install Oppleo on a Raspberry Pi 4

#### Prereqs
  * I run Oppleo on a __Raspberry Pi 4__. I have not tested other versions, I can only assume a 3 would work too. If you need to order one, get a 4, if you have one laying around give it a try.
  * You'll need a __SmartEVSE__ to control the actual car charging. Oppleo pulls a pin down to enable/disable charging, so any other EVSE with a similar control pin might work.
  * `ssh` enabled on the Raspberry. 
    * Add an empty file named `ssh` (no extension) to the root of the sdcard to enable ssh after boot on the Raspberry. You'll probably need ssh to install Python and Postgress anyway.
  * Make sure __apt-get__ is up to date  
    > `sudo apt-get update && sudo apt-get upgrade`
  * git installed on your Raspberry
    > `sudo apt-get install git`
  * __RFID reader, mult-color LED, Buzzer, and Real-Time Clock__. Technically not needed, but makes for better experience. Make sure they are on the GPIO PINs as per diagram, or change the configuration accordingly.
    * A Raspberry does not come with a Real-Time Clock (RTC). [Read up](https://thepihut.com/blogs/raspberry-pi-tutorials/17209332-adding-a-real-time-clock-to-your-raspberry-pi) to understand if you want one.
      * Install [RasClock](https://afterthoughtsoftware.com/products/rasclock) (Real Time Clock)
      * Check it it is installed using `sudo hwclock -r`
      * Start after boot `sudo nano /boot/config.txt` add
        > `# RasClock RealTime Clock`  
        > `dtoverlay=i2c-rtc,pcf2127`
        * Reboot your Raspberry
        > `sudo reboot`
  * __Pyhton3__ and __pip__ installed on the Raspberry
    > `sudo apt-get install python3-dev python3-pip`
  * __Postgres__ database installed on your Raspberry
    * (Google for [How-to](https://opensource.com/article/17/10/set-postgres-database-your-raspberry-pi)'s) 
    * Have an empty database ready, with a user with the proper read-write rights to that database, and know the password.
  * Install __spidev__ for interfacing with SPI devices. This is required to interface with the RFID reader which uses the SPI bus.
    * Install the C library
      > `cd /home/pi`  
      > `git clone https://github.com/lthiery/SPI-Py.git`   
      > `cd SPI-Py`  
      > `sudo python3 setup.py install`
    * Install the pyhton module
      > `sudo pip3 install spidev`  
    * Enable SPI and the PCM at boot. 
      * Edit /boot/config.txt
        > `sudo nano /boot/config.txt`
      * Add these lines
        > `dtparam=spi=on` 
        > `dtoverlay=spi-bcm2708`
    * Check if properly instaled
      > `lsmod | grep spi`
      * should return something like
        > `spidev                 20480  0`  
        > `spi_bcm2835            20480  0`
  * Install mfrc522, the interface module for the RFID reader.
    * ~~Install the SimpleMFRC522 library
      > ~~`cd /home/pi`  
      > ~~`git clone https://github.com/pimylifeup/MFRC522-python`  
      > ~~`sudo python3 setup.py install`
    * Install SimpleMFRC522 from PyPi (same package as listed above)  
      > `sudo pip3 install mfrc522`
  * Install RPi.GPIO, a PyPi python module for interfacing with the Raspberry Gneral Purpose IO (GPPIO) pins. This is required to interface with the RTC, LED, the Buzzer, and the SmartEVSE.
    > `sudo pip install RPi.GPIO`
  * Install mimimalmodbus, used to communicate with the kWh meter
    > `pip3 install -U minimalmodbus`
    * reboot
      > `sudo reboot`
    * and check if the modbus interface is foundShow USB devices. Use
      > `lsusb`
    * to check the USB hub, and 
      > `usb-devices`
    * to get a list of USB devices. 

      
  
 #### Installation
 Oppleo is not a nicely packaged resource. Basically you'll pull the developer code and run that. 
 Use ssh to login to the Raspberry. You'' end up in `/home/pi`
 
 * Clone the __Oppleo__ repo in the `/home/pi` folder (note: get the URL from the Clone or Download button above!)
 > `git clone https://github.com/ilseh/Oppleo.git`
 * Move into the Oppleo directory
 > `cd Oppleo`
 * Create a virtual environment for Oppleo
 > `python3 -m venv venv`
 * Activate it
	> `source venv/bin/activate`
 * Upgrade pip (if required)
	> `pip install --upgrade pip`
 * Install all dependencies from the requirements_raspberry.txt file
	> `pip install -r requirements_raspberry.txt`
 * Create an Oppleo ini file 
 > `cp /home/pi/Oppleo/src/nl/oppleo/config/oppleo.example.ini /home/pi/Oppleo/src/nl/oppleo/config/oppleo.ini`
 * Edit the oppleo ini file to reflect your installation. The example ini file has comments to help. Note that this ini file is overwritten when settings are changed through Oppleos webfront, so remarks etc. will be lost.
   * All elements are in the [Oppleo] section. All `True` and `False` are Python, thus capitalize the first letter.
   * `signature` is a random generated signature to identify this application when logging or sending messages through Prowl. 
   * `database_url` is `postgresql://USER:PASSWORD@IPADRESS:5432/DATABASE` where USER, PASSWORD, IPADDRESS, and DATABASE are your own values.
   * `sqlalchemy_track_modifications` should be `False` 
   * `env` should be `Production`
   * `debug` should be `False`
   * `testing` should be `False`
   * `pythonpath` is empty
   * `explain_template_loading` provides a debug information on screen if something goes wrong internally. `False` should be better. 
   * The `on_db_failure_` variables come into play if the database cannot be reached by Oppleo. It becomes blind to settings, and thus some fallback settings are required.
     * `on_db_failure_allow_restart` provides a restart button when `True`
     * `on_db_failure_magic_password` is password to enter when making changes on a database failure. Set it through the web front. Looks like `pbkdf2:sha256:<some long string>`
     * `on_db_failure_allow_url_change` allows the database URL to be changed after a failure, could be caused by misconfiguration, through the web front if `True`. Set this to `True` untill it is all working and then set it to `False`, or leave at `True` if security is not an issue.  
     * `on_db_failure_show_current_url` shows the database URL through the web front even if no connection could be made. Shows your database username and password when `True`, so be carefull. 
   
 
 * Install Oppleo as a service (creates a Oppleo.service file in /etc/systemd/system/ and reloads systemctl)
 > `install/install.sh`

Oppleo should now be running. Check http://localhost/ or the IP address of the raspberry.

After installing Oppleo:
  * go to settings in the webfront and change them. Not all settings are changeable in the web front, for some you'll have to update the database. Tables:
    * `charger_config` for general configurations
    * `energy_device` for the modbus settings
    * `off_peak_hours` for the recurring weekdays, the holidays can be changed through the webfront 
  * The default username/password is admin/admin. Through the web front only the password can be changed. There is are no other users implemented, however adding users manually to the database should work. There are no roles.
  * You can restart Oppleo through the webapp, even restart or shutdown the Pi. Use this when powering the Pi off. I have been looking into a UPS for the Pi, as earlier versions shewed my sdcards on reboot more than once. The Pi 4 however has been nice to the sdcard on power cycles.
  * Oppleo logs to `/tmp/Oppleo.log`


___

## Some Developer specific references
> `sudo apt-get install libpq-dev`  
> `sudo apt install python3.6-dev`  
> `sudo apt-get install build-essential`  

> `install liquibase`
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


