# Reaspberry config
echo "Install script for the Oppleo service"
echo "v0.3 06-03-2020"

# Some systemd commands
# 1. systemd version
#   systemd --version
# 2. Check if systemd is runnign or not
#   ps -eaf | grep [s]ystemd
# 3. Analyze systemd boot process
#   systemd-analyze
# 4. Analyze time taken by each process at boot
#   systemd --version

# Check prereq: is Pi GPIO Daemon (pigpiod) installed and running? 
echo "Checking prereqs: is Pi GPIO Daemon (pigpiod) installed and running?"
IFS=' ' # space is set as delimiter
read -ra pigpiodSysdEntry <<< $(systemctl list-unit-files --type=service | grep pigpiod)
if [ "${#pigpiodSysdEntry[@]}" -gt 0 ]; then
  echo "  found pigpiod, it is "${pigpiodSysdEntry[1]}
  if [ ${pigpiodSysdEntry[1]} !=  "enabled" ]; then
    echo "  enabling Pi GPIO Daemon (pigpiod)..."
    sudo systemctl enable pigpiod.service
    echo "  starting Pi GPIO Daemon (pigpiod)..."
    sudo systemctl start pigpiod.service
    if (!(systemctl -q is-active pigpiod.service)); then
      echo "  Pi GPIO Daemon (pigpiod) not running."
      systemctl list-unit-files --type=service | grep pigpiod
      echo "Install failed"
      exit 1
    fi
  fi
else
  # Pi GPIO Daemon is apparently not installed
  echo "  installing Pi GPIO Daemon..."
  # Remove old versions
  rm /home/pi/pigpio.zip
  sudo rm -rf /home/pi/PIGPIO
  # Download 
  wget abyz.me.uk/rpi/pigpio/pigpio.zip -P /home/pi/
  unzip /home/pi/pigpio.zip
  cwd=$(pwd)
  cd /home/pi/PIGPIO
  make
  sudo make install
  # Return to current working directory
  cd $(cwd)
  echo "  Pi GPIO Daemon installed."
  echo "  enabling Pi GPIO Daemon (pigpiod)..."
  sudo systemctl enable pigpiod.service
  echo "  starting Pi GPIO Daemon (pigpiod)..."
  sudo systemctl start pigpiod.service
fi
echo "  done checking pigpiod prereq."

echo "Installing the Oppleo systemd service..."
echo " determining the location of the install script..."
# DIR holds the directory of oppleo
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo " install script in dir $DIR..."
# PRJDIR holds the root directory of rhe project
PRJDIR=${DIR%"/oppleo"}
echo " project root $PRJDIR..."
echo " activate virtual environment..."
source $PRJDIR/venv/bin/activate
echo " make sure pip is up to date..."
pip install --upgrade pip > /dev/null 2>&1
echo " install psycopg2..."
pip install psycopg2-binary > /dev/null 2>&1
echo " set SSL library for C compiler..."
export LDFLAGS="-L/usr/local/opt/openssl/lib"
# Check if this is on a Raspberry
raspberry=false
if [ -f '/proc/cpuinfo' ]; then
    if grep -q 'Raspberry' /proc/cpuinfo; then
        raspberry=true
    fi
fi
if [ "$raspberry" = true ]; then
    echo " On a raspberry :)"
    echo " - installing raspberry dependencies incl mfrc522, RPi.GPIO, and spidev..."
    pip install -r $PRJDIR/requirements_raspberry.txt > /dev/null 2>&1
    echo " - preparing service file Oppleo.service from template by updating path..."
    sed 's?#WORKINGDIR_PLACEHOLDER?'$PRJDIR'?'g < $DIR/Oppleo.service.template >$DIR/Oppleo.service
    echo " - stopping Oppleo if running..."
    sudo systemctl stop Oppleo.service
    echo " - Update config/ installing Oppleo.service for systemd..."
    sudo cp $DIR/Oppleo.service /etc/systemd/system/Oppleo.service
    echo " - reloading daemon config..."
    sudo systemctl daemon-reload
    echo " - starting Oppleo systemd daemon..."
    sudo systemctl start Oppleo.service
    sudo systemctl status Oppleo.service
else
    echo " Not on a raspberry..."
    echo " - installing dependencies without mfrc522, RPi.GPIO, and spidev..."
    pip install -r $PRJDIR/requirements_non_raspberry.txt > /dev/null 2>&1
    echo " - not installing the service."
fi
echo "Done!"
