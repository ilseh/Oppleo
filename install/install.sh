#!/bin/bash

# Reaspberry config
echo "Install script for the Oppleo service"
echo "v0.6.7 05-05-2021"
 
echo "Running install script as $(whoami)"
echo "Using background restart at the end."
echo "PATH=$PATH"


# Some systemd commands
# 1. systemd version
#   systemd --version
# 2. Check if systemd is runnign or not
#   ps -eaf | grep [s]ystemd
# 3. Analyze systemd boot process
#   systemd-analyze
# 4. Analyze time taken by each process at boot
#   systemd --version
 

# Define all variables
function init() {
  echo " init - Start"

  # Initiated from cmd line or from online?
  [[ $1 == "online" ]] && ONLINE=true || ONLINE=false

  # Check if systemctl is present (should be present)
  #  0 (true)  - present
  #  1 (false) - not present
  SYSTEMCTL_PRESENT=$(command -v systemctl &> /dev/null; echo "$?")
  if [ "$SYSTEMCTL_PRESENT" = true ] || [ "$SYSTEMCTL_PRESENT" -eq 0 ]; then
    echo "  systemctl is present"
  else
    echo "  systemctl is not present"
  fi

  # Check if this is a raspberry
  #  0 (true)  - on raspberry
  #  1 (false) - not on raspberry
  ON_RASPBERRY=false
  if [ -f '/proc/cpuinfo' ]; then
      if grep -q 'Raspberry' /proc/cpuinfo; then
          ON_RASPBERRY=true
          echo "  On a Raspberry Pi!"
      fi
  fi

  echo "  Determining the current working directory..."
  CURRENT_WORKING_DIR=$(pwd)
  echo "   -> $CURRENT_WORKING_DIR"

  echo "  Determining the location of the install script..."
  # INSTALL_SCRIPT_DIR holds the directory of oppleo install script
  INSTALL_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
  echo "  -> $INSTALL_SCRIPT_DIR"
  echo "  Determining the Oppleo root directory..."
  # OPPLEO_ROOT_DIR holds the root directory of the project
  OPPLEO_ROOT_DIR=${INSTALL_SCRIPT_DIR%"/install"}
  echo "  -> $OPPLEO_ROOT_DIR"

  # Check if there is a virual env active, if so keep that active on exit
  # - in venv : INVENV=1
  # - in venv : INVENV=0
  [[ "$VIRTUAL_ENV" == "" ]]; INVENV=$?
  if [ "$INVENV" -eq 1 ]; then
    echo "  Virtual environment active ($VIRTUAL_ENV)"
  else 
    echo "  Not in virtual environment"
  fi

    # systemctl is-active --quiet service
  # will exit with status zero if service is active, non-zero otherwise
  if [ "$SYSTEMCTL_PRESENT" == true ] || [ "$SYSTEMCTL_PRESENT" == 0 ]; then
    systemctl is-active --quiet Oppleo.service
    if [ "$?" -eq 0 ]; then
      # Oppleo running 
      START_OPPLEO_SERVICE=true
    fi
  fi

  echo "  set SSL library for C compiler..."
  export LDFLAGS="-L/usr/local/opt/openssl/lib"

  echo " init - Done"
}


# Argument $1 to indicate on Raspberry
# Argument $2 to indicate systemctl present
function stopService( ) {
  echo " stopService - Start"
  
  # Are we on a raspberry? 
  if [ "$1" == false ] || [ "$1" == 1 ]; then
    echo "  Not on Raspberry, no Oppleo.service to stop."
    echo " stopService - Done (-1)"
    return -1
  fi
  # Is systemctl available? 
  if [ "$2" == false ] || [ "$2" == 1 ]; then
    echo "  No systemctl available, no Oppleo.service to stop."
    echo " stopService - Done (-2)"
    return -2
  fi

  if [ "$START_OPPLEO_SERVICE" == true ]; then
    # Oppleo running 
    if [ "$ONLINE" == true ]; then
      echo "  Not stopping Oppleo (is running), this kills calling process..."
    else
      echo "  Stopping Oppleo (is running)..."
      sudo systemctl stop Oppleo.service
    fi
  else
    # Oppleo not running 
    echo "  Oppleo is not running..."
  fi

  echo " stopService - Done"
}


# Argument $1 to indicate on Raspberry
# Argument $2 to indicate systemctl present
function checkPiGPIO( ) {
  echo " checkPiGPIO - Start"
  
  # Are we on a raspberry? 
  if [ "$1" == false ] || [ "$1" == 1 ]; then
    echo "  Not on Raspberry, no Pi GPIO Daemon (pigpiod) to check."
    echo " checkPiGPIO - Done (-1)"
    return -1
  fi
  # Is systemctl available? 
  if [ "$2" == false ] || [ "$2" == 1 ]; then
    echo "  No systemctl available, no Pi GPIO Daemon (pigpiod) to check."
    echo " checkPiGPIO - Done (-2)"
    return -2
  fi

  # Check prereq: is Pi GPIO Daemon (pigpiod) installed and running? 
  echo "  Checking prereqs: is Pi GPIO Daemon (pigpiod) installed and running?"
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
        echo "  Install failed"
        echo " checkPiGPIO - Done (-3)"
        return -3
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

  echo " checkPiGPIO - Done"
}


function checkVirtualEnv() {
  echo " checkVirtualEnv - Start"

  if [[ $INENV -eq 1 ]]; then
    echo "  In active virtual environment ($VIRTUAL_ENV)"
    echo " checkVirtualEnv - Done (0)"
    return 0
  fi
  # Not in an active venv, any present?
  if [ ! -f "$OPPLEO_ROOT_DIR/venv/bin/activate" ]; then
      echo "  Virtual env does not exist. Creating..."
      cd $OPPLEO_ROOT_DIR
      python3 -m venv venv
      echo "  Virtual created."
  fi
  echo "  Activate virtual environment..."
  source $OPPLEO_ROOT_DIR/venv/bin/activate
  echo "  Virtual environment activated ($VIRTUAL_ENV)"

  echo " checkVirtualEnv - Done"
}


# Argument $1 to indicate on Raspberry
# Argument $2 to indicate systemctl present
function installPsycopg2( ) {
  echo " installPsycopg2 - Start"
  
  # Are we on a raspberry? 
  if [ "$1" == false ] || [ "$1" == 1 ]; then
    echo "  Not on Raspberry, no psycopg2 to check."
    echo " installPsycopg2 - Done (-1)"
    return -1
  fi
  echo "  Installing psycopg2..."
  pip install psycopg2-binary > /dev/null 2>&1

  echo " installPsycopg2 - Done"
}


# Argument $1 to indicate on Raspberry
# Argument $2 to indicate systemctl present
function installSystemdService( ) {
  echo " installSystemdService - Start"
  
  echo "  Preparing service file Oppleo.service from template by updating path..."
  sed 's?#WORKINGDIR_PLACEHOLDER?'$OPPLEO_ROOT_DIR'?'g < $INSTALL_SCRIPT_DIR/Oppleo.service.template >$INSTALL_SCRIPT_DIR/Oppleo.service

  # Are we on a raspberry? 
  if [ "$1" == false ] || [ "$1" == 1 ]; then
    echo "  Not on Raspberry, skipping Oppleo systemd service file installation."
    echo " installSystemdService - Done (-1)"
    return -1
  fi
  # Is systemctl available? 
  if [ "$2" == false ] || [ "$2" == 1 ]; then
    echo "  No systemctl available, skipping Oppleo systemd service file installation."
    echo " installSystemdService - Done (-2)"
    return -2
  fi

  # Check if service file exists
  if [ -f /etc/systemd/system/Oppleo.service ]; then
    echo "  The Oppleo systemd service file exists."
    echo " installSystemdService - Done (0)"
    return 0
  fi

  echo "  Installing the Oppleo systemd service..."

  echo "  - Update config/ installing Oppleo.service for systemd..."
  sudo cp $INSTALL_SCRIPT_DIR/Oppleo.service /etc/systemd/system/Oppleo.service
  echo "  - reloading daemon config..."
  sudo systemctl daemon-reload
  echo "  - enabling the Oppleo.service (auto start)..."
  sudo systemctl enable Oppleo.service
  # New, so start
  START_OPPLEO_SERVICE=true

  echo " installSystemdService - Done"

}

# Argument $1 to indicate on Raspberry
# Argument $2 to indicate systemctl present
function startSystemdService( ) {
  echo " startSystemdService - Start"
  
  # Are we on a raspberry? 
  if [ "$1" == false ] || [ "$1" == 1 ]; then
    echo "  Not on Raspberry, not starting Oppleo systemd service."
    echo " startSystemdService - Done (-1)"
    return -1
  fi
  # Is systemctl available? 
  if [ "$2" == false ] || [ "$2" == 1 ]; then
    echo "  No systemctl available, not starting Oppleo systemd service."
    echo " startSystemdService - Done (-2)"
    return -2
  fi

  # Check if service file exists
  if [ "$START_OPPLEO_SERVICE" == true ]; then
    echo "  Restart the Oppleo systemd service in 2 seconds in the background..."
    (sleep 2; sudo systemctl restart Oppleo.service) &
  else
    echo "  Oppleo systemd service was not running, not starting it now."
    echo "   [MANUAL] sudo systemctl start Oppleo.service"
  fi

  echo " startSystemdService - Done"
}



# Argument $1 to indicate on Raspberry
# Argument $2 to indicate systemctl present
function installPipDependencies( ) {
  echo " installPipDependencies - Start"
  
  echo "  make sure pip is up to date..."
  pip install --upgrade pip > /dev/null 2>&1

  # Are we on a raspberry? 
  if [ "$1" == false ] || [ "$1" == 1 ]; then
    echo "  installing non-raspberry dependencies excl. mfrc522, RPi.GPIO, and spidev..."
    pip install -r $OPPLEO_ROOT_DIR/requirements_non_raspberry.txt > /dev/null 2>&1
  else
    echo "  installing raspberry dependencies incl mfrc522, RPi.GPIO, and spidev..."
    pip install -r $OPPLEO_ROOT_DIR/requirements.txt > /dev/null 2>&1
  fi

  echo " installPipDependencies - Done"
}


function gitUpdate( ) {
  echo " gitUpdate - Start"
  
  echo "  update from git (git pull)..."
  # (cd $OPPLEO_ROOT_DIR && git --git-dir=/home/pi/Oppleo/.git --work-tree=/home/pi/Oppleo pull &> /dev/null)
  (cd $OPPLEO_ROOT_DIR && git --git-dir=$OPPLEO_ROOT_DIR/.git --work-tree=$OPPLEO_ROOT_DIR pull)
  EXITCODE=$?
  if [ "$EXITCODE" == 0 ]; then
    echo "  Git pull succeeded ($EXITCODE)"
  else
    echo "  Git pull FAILED! (exitcode $EXITCODE)"
  fi

  echo " gitUpdate - Done"

  return $EXITCODE
}


function updateDatabase( ) {
  echo " updateDatabase - Start"

  echo "  get liquibase location..."
  lbpath=$(cat ~/.bashrc | grep liquibase | cut -d':' -f2)
  echo "  liquibase at $lbpath"

  echo "  Release liquibase locks..."
  # (cd $OPPLEO_ROOT_DIR/db && liquibase releaseLocks &> /dev/null)
  (cd $OPPLEO_ROOT_DIR/db && $lbpath/liquibase releaseLocks)
  EXITCODE=$?
  if [ "$EXITCODE" == 0 ]; then
    echo "  Success ($EXITCODE)"
  else
    echo "  FAILED! (exitcode $EXITCODE)"
  fi
  echo "  Run liquibase update..."
  # make sure the workling dir is changed. The parentheses spawn a subshell)
  # (cd $OPPLEO_ROOT_DIR/db && liquibase update &> /dev/null)
  (cd $OPPLEO_ROOT_DIR/db && $lbpath/liquibase update)
  EXITCODE=$?
  if [ "$EXITCODE" == 0 ]; then
    echo "  Success ($EXITCODE)"
  else
    echo "  FAILED! (exitcode $EXITCODE)"
  fi
 
  echo " updateDatabase - Done"
}

# Cleanup
function cleanup() {
  echo " cleanup - Start"

  # Deactivate the venv if it wasn't active at start
  # if [ $INVENV -ne 1 ]; then
  #   echo "  Deactivate active virtual environment ($VIRTUAL_ENV)..."
  #   deactivate
  # fi

  # go back to the original working dir
  # echo '  Changing back to original working directory...'
  # cd $CURRENT_WORKING_DIR

  echo " cleanup - Done"
}



# 1. Determine the parameters
init $1
# Check and install prerequisites
# 2. Deactivate Oppleo service if running
stopService $ON_RASPBERRY $SYSTEMCTL_PRESENT
# 3. is there a virtual environment? If not, create one, and activate
checkVirtualEnv
# 4. Is Pi GPIO Daemon (pigpiod) installed and running? 
checkPiGPIO $ON_RASPBERRY $SYSTEMCTL_PRESENT

# 5. Update from github
gitUpdate

# 6. Update PIP and install dependencies
installPipDependencies $ON_RASPBERRY

# 7. Update database
updateDatabase

# 8. 
installPsycopg2 $ON_RASPBERRY
#    Is Pi GPIO Daemon (pigpiod) installed and running? 
#    Is Pi GPIO Daemon (pigpiod) installed and running? 

# 9. Install the Oppleo service (Oppleo.service & enable)
installSystemdService $ON_RASPBERRY $SYSTEMCTL_PRESENT

# 10. Start Oppleo service (if already started or non-existend)
startSystemdService $ON_RASPBERRY $SYSTEMCTL_PRESENT

# 11. Deactivate venv if not active at start, and go back to the working dir
cleanup


echo "Done!"
