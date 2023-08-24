#!/bin/bash

RED='\033[0;31;1m'
GREEN='\033[0;32;1m'
BLUE='\033[0;34;1m'
CYAN='\033[0;36;1m'
NC='\033[0m'
CHECKMARK='\xE2\x9C\x94'

# Reaspberry config
printf "Install script for the Oppleo service - v0.8 20-02-2022 \n"
 
printf " [i] Running install script as $(whoami) \n"
printf " [i] Using background restart at the end. \n"
printf " [i] PATH=$PATH \n"


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
  printf " [i] init - Start \n"

  # Initiated from cmd line or from online?
  [[ $1 == "online" ]] && ONLINE=true || ONLINE=false
  if [ "$ONLINE" == true ]; then
    printf " [i] Update process initiated from the Oppleo.service process (online) \n"
  else
    printf " [i] Update process initiated from a command line \n"
  fi

  # Check if systemctl is present (should be present)
  #  0 (true)  - present
  #  1 (false) - not present
  SYSTEMCTL_PRESENT=$(command -v systemctl &> /dev/null; printf "$?")
  if [ "$SYSTEMCTL_PRESENT" = true ] || [ "$SYSTEMCTL_PRESENT" -eq 0 ]; then
    printf " [${GREEN}${CHECKMARK}${NC}] systemctl is present \n"
  else
    printf " [i] systemctl is not present \n"
  fi

  # Check if this is a raspberry
  #  0 (true)  - on raspberry
  #  1 (false) - not on raspberry
  ON_RASPBERRY=false
  if [ -f '/proc/cpuinfo' ]; then
      if grep -q 'Raspberry' /proc/cpuinfo; then
          ON_RASPBERRY=true
          printf " [${GREEN}${CHECKMARK}${NC}] On a Raspberry Pi! \n"
      fi
  fi

  printf " [i] Determining the current working directory... \n"
  CURRENT_WORKING_DIR=$(pwd)
  printf " [${GREEN}${CHECKMARK}${NC}] -> $CURRENT_WORKING_DIR \n"

  printf " [i] Determining the location of the install script... \n"
  # INSTALL_SCRIPT_DIR holds the directory of oppleo install script
  INSTALL_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
  printf " [${GREEN}${CHECKMARK}${NC}] -> $INSTALL_SCRIPT_DIR \n"
  printf " [i] Determining the Oppleo root directory... \n"
  # OPPLEO_ROOT_DIR holds the root directory of the project
  OPPLEO_ROOT_DIR=${INSTALL_SCRIPT_DIR%"/install"}
  printf " [${GREEN}${CHECKMARK}${NC}] $OPPLEO_ROOT_DIR \n"

  # Check if there is a virual env active, if so keep that active on exit
  # - in venv : INVENV=1
  # - in venv : INVENV=0
  [[ "$VIRTUAL_ENV" == "" ]]; INVENV=$?
  if [ "$INVENV" -eq 1 ]; then
    printf " [${GREEN}${CHECKMARK}${NC}] Virtual environment active ($VIRTUAL_ENV) \n"
  else 
    printf " [${CYAN}-${NC}] Not in virtual environment \n"
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

  printf " [i] set SSL library for C compiler... \n"
  export LDFLAGS="-L/usr/local/opt/openssl/lib \n"

  printf " [${GREEN}${CHECKMARK}${NC}] init - Done \n"
}


# Argument $1 to indicate on Raspberry
# Argument $2 to indicate systemctl present
function stopService( ) {
  printf " [i] stopService - Start \n"
  
  # Are we on a raspberry? 
  if [ "$1" == false ] || [ "$1" == 1 ]; then
    printf " [${CYAN}-${NC}] Not on Raspberry, no Oppleo.service to stop. \n"
    printf " [${GREEN}${CHECKMARK}${NC}] stopService - Done (-1) \n"
    return -1
  fi
  # Is systemctl available? 
  if [ "$2" == false ] || [ "$2" == 1 ]; then
    printf " [${CYAN}-${NC}] No systemctl available, no Oppleo.service to stop. \n"
    printf " [${GREEN}${CHECKMARK}${NC}] stopService - Done (-2) \n"
    return -2
  fi

  if [ "$START_OPPLEO_SERVICE" == true ]; then
    # Oppleo running 
    if [ "$ONLINE" == true ]; then
      printf " [i] Not stopping Oppleo (is running), this kills calling process... \n"
    else
      printf " [i] Stopping Oppleo (is running)... \n"
      sudo systemctl stop Oppleo.service
      printf " [${GREEN}${CHECKMARK}${NC}] Oppleo stopped \n"
    fi
  else
    # Oppleo not running 
    printf " [${CYAN}-${NC}] Oppleo is not running... \n"
  fi

  printf " [${GREEN}${CHECKMARK}${NC}] stopService - Done \n"
}


# Argument $1 to indicate on Raspberry
# Argument $2 to indicate systemctl present
function checkPiGPIO( ) {
  printf " [i] checkPiGPIO - Start \n"
  
  # Are we on a raspberry? 
  if [ "$1" == false ] || [ "$1" == 1 ]; then
    printf " [${CYAN}-${NC}] Not on Raspberry, no Pi GPIO Daemon (pigpiod) to check. \n"
    printf " [${GREEN}${CHECKMARK}${NC}] checkPiGPIO - Done (-1) \n"
    return -1
  fi
  # Is systemctl available? 
  if [ "$2" == false ] || [ "$2" == 1 ]; then
    printf " [${CYAN}-${NC}] No systemctl available, no Pi GPIO Daemon (pigpiod) to check. \n"
    printf " [${GREEN}${CHECKMARK}${NC}] checkPiGPIO - Done (-2) \n"
    return -2
  fi

  # Check prereq: is Pi GPIO Daemon (pigpiod) installed and running? 
  printf " [i] Checking prereqs: is Pi GPIO Daemon (pigpiod) installed and running? \n"
  IFS=' ' # space is set as delimiter
  read -ra pigpiodSysdEntry <<< $(systemctl list-unit-files --type=service | grep pigpiod)
  if [ "${#pigpiodSysdEntry[@]}" -gt 0 ]; then
    printf " [${GREEN}${CHECKMARK}${NC}] found pigpiod, it is "${pigpiodSysdEntry[1]}"\n"
    if [ ${pigpiodSysdEntry[1]} !=  "enabled" ]; then
      printf " [i] enabling Pi GPIO Daemon (pigpiod)... \n"
      sudo systemctl enable pigpiod.service
      printf " [i] starting Pi GPIO Daemon (pigpiod)... \n"
      sudo systemctl start pigpiod.service
      if (!(systemctl -q is-active pigpiod.service)); then
        printf " [${CYAN}-${NC}] Pi GPIO Daemon (pigpiod) not running. \n"
        systemctl list-unit-files --type=service | grep pigpiod
        printf " [${RED}x${NC}] ${RED}Pi GPIO Daemon install failed!${NC} \n"
        printf " [${GREEN}${CHECKMARK}${NC}]  checkPiGPIO - Done (-3) \n"
        return -3
      fi
    fi
  else
    # Pi GPIO Daemon is apparently not installed
    printf " [i] installing Pi GPIO Daemon... \n"
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
    printf " [${GREEN}${CHECKMARK}${NC}] Pi GPIO Daemon installed. \n"
    printf " [i] enabling Pi GPIO Daemon (pigpiod)... \n"
    sudo systemctl enable pigpiod.service
    printf " [i] starting Pi GPIO Daemon (pigpiod)... \n"
    sudo systemctl start pigpiod.service
  fi

  printf " [${GREEN}${CHECKMARK}${NC}] checkPiGPIO - Done \n"
}


function checkVirtualEnv() {
  printf " [i] checkVirtualEnv - Start \n"

  if [[ $INENV -eq 1 ]]; then
    printf " [${GREEN}${CHECKMARK}${NC}] In active virtual environment ($VIRTUAL_ENV) \n"
    printf " [${GREEN}${CHECKMARK}${NC}] checkVirtualEnv - Done (0) \n"
    return 0
  fi
  # Not in an active venv, any present?
  if [ ! -f "$OPPLEO_ROOT_DIR/venv/bin/activate" ]; then
      printf " [${CYAN}-${NC}] Virtual env does not exist. Creating... \n"
      cd $OPPLEO_ROOT_DIR
      python3 -m venv venv
      printf " [${GREEN}${CHECKMARK}${NC}] Virtual created. \n"
  fi
  printf " [i] Activate virtual environment... \n"
  source $OPPLEO_ROOT_DIR/venv/bin/activate
  printf " [${GREEN}${CHECKMARK}${NC}] Virtual environment activated ($VIRTUAL_ENV) \n"

  printf " [${GREEN}${CHECKMARK}${NC}] checkVirtualEnv - Done \n"
}


# Argument $1 to indicate on Raspberry
# Argument $2 to indicate systemctl present
function installPsycopg2( ) {
  printf " [i] installPsycopg2 - Start \n"
  
  # Are we on a raspberry? 
  if [ "$1" == false ] || [ "$1" == 1 ]; then
    printf " [${CYAN}-${NC}] Not on Raspberry, no psycopg2 to check. \n"
    printf " [${GREEN}${CHECKMARK}${NC}] installPsycopg2 - Done (-1) \n"
    return -1
  fi
  printf " [i] Installing psycopg2... \n"
  pip install psycopg2-binary > /dev/null 2>&1

  printf " [${GREEN}${CHECKMARK}${NC}] installPsycopg2 - Done \n"
}


# Argument $1 to indicate on Raspberry
# Argument $2 to indicate systemctl present
function installSystemdService( ) {
  printf " [i] installSystemdService - Start \n"
  
  printf " [i] Preparing service file Oppleo.service from template by updating path... \n"
  sed 's?#WORKINGDIR_PLACEHOLDER?'$OPPLEO_ROOT_DIR'?'g < $INSTALL_SCRIPT_DIR/Oppleo.service.template >$INSTALL_SCRIPT_DIR/Oppleo.service

  # Are we on a raspberry? 
  if [ "$1" == false ] || [ "$1" == 1 ]; then
    printf " [${CYAN}-${NC}] Not on Raspberry, skipping Oppleo systemd service file installation. \n"
    printf " [${GREEN}${CHECKMARK}${NC}] installSystemdService - Done (-1) \n"
    return -1
  fi
  # Is systemctl available? 
  if [ "$2" == false ] || [ "$2" == 1 ]; then
    printf " [${CYAN}-${NC}] No systemctl available, skipping Oppleo systemd service file installation. \n"
    printf " [${GREEN}${CHECKMARK}${NC}] installSystemdService - Done (-2) \n"
    return -2
  fi

  # Check if service file exists
  #if [ -f /etc/systemd/system/Oppleo.service ]; then
  #  printf "  The Oppleo systemd service file exists. \n"
  #  printf " installSystemdService - Done (0) \n"
  #  return 0
  #fi

  printf " [i] Installing the Oppleo systemd service... \n"

  printf " [i] Update config/ installing Oppleo.service for systemd... \n"
  sudo cp $INSTALL_SCRIPT_DIR/Oppleo.service /etc/systemd/system/Oppleo.service
  printf " [i] reloading daemon config... \n"
  sudo systemctl daemon-reload
  printf " [i] enabling the Oppleo.service (auto start)... \n"
  sudo systemctl enable Oppleo.service
  # New, so start
  START_OPPLEO_SERVICE=true

  printf " [${GREEN}${CHECKMARK}${NC}] installSystemdService - Done \n"

}

# Argument $1 to indicate on Raspberry
# Argument $2 to indicate systemctl present
function startSystemdService( ) {
  printf " [i] startSystemdService - Start \n"
  
  # Are we on a raspberry? 
  if [ "$1" == false ] || [ "$1" == 1 ]; then
    printf " [${CYAN}-${NC}] Not on Raspberry, not starting Oppleo systemd service. \n"
    printf " [${GREEN}${CHECKMARK}${NC}] startSystemdService - Done (-1) \n"
    return -1
  fi
  # Is systemctl available? 
  if [ "$2" == false ] || [ "$2" == 1 ]; then
    printf " [${CYAN}-${NC}] No systemctl available, not starting Oppleo systemd service. \n"
    printf " [${GREEN}${CHECKMARK}${NC}] startSystemdService - Done (-2) \n"
    return -2
  fi

  # Check if service file exists
  if [ "$START_OPPLEO_SERVICE" == true ]; then
    if [ "$ONLINE" == true ]; then
      printf " [i] Restart the Oppleo systemd service in 2 seconds in the background... \n"
      (sleep 2; sudo systemctl restart Oppleo.service) &
    else
      printf " [i] Start the Oppleo systemd service... \n"
      sudo systemctl start Oppleo.service
      # systemctl is-active --quiet service
      # will exit with status zero if service is active, non-zero otherwise
      systemctl is-active --quiet Oppleo.service
      if [ "$?" -eq 0 ]; then
        # Oppleo running 
        printf " [${GREEN}${CHECKMARK}${NC}] Oppleo systemd service running \n"
      else
        printf " [${RED}x${NC}] ${RED}Starting the Oppleo systemd service failed!${NC} \n"
        sudo systemctl status Oppleo.service
      fi
    fi
  else
    printf " [i] Oppleo systemd service was not running, not starting it now. \n"
    printf " [i] [MANUAL] sudo systemctl start Oppleo.service \n"
  fi

  printf " [${GREEN}${CHECKMARK}${NC}] startSystemdService - Done \n"
}



# Argument $1 to indicate on Raspberry
# Argument $2 to indicate systemctl present
function installPipDependencies( ) {
  printf " [i] installPipDependencies - Start \n"
  
  printf " [i] make sure pip is up to date... \n"
  pip install --upgrade pip > /dev/null 2>&1

  # Are we on a raspberry? 
  if [ "$1" == false ] || [ "$1" == 1 ]; then
    printf " [i] installing non-raspberry dependencies excl. mfrc522, RPi.GPIO, and spidev... \n"
    pip install -r $OPPLEO_ROOT_DIR/requirements_non_raspberry.txt > /dev/null 2>&1
  else
    printf " [i] installing raspberry dependencies incl mfrc522, RPi.GPIO, and spidev... \n"
    pip install -r $OPPLEO_ROOT_DIR/requirements.txt > /dev/null 2>&1
  fi

  printf " [${GREEN}${CHECKMARK}${NC}] installPipDependencies - Done \n"
}


function gitUpdate( ) {
  printf " [i] gitUpdate - Start \n"
  
  printf " [i] update from git (git pull)... \n"
  # (cd $OPPLEO_ROOT_DIR && git --git-dir=/home/pi/Oppleo/.git --work-tree=/home/pi/Oppleo pull &> /dev/null)
  # (cd $OPPLEO_ROOT_DIR && git --git-dir=$OPPLEO_ROOT_DIR/.git --work-tree=$OPPLEO_ROOT_DIR pull)
  (cd $OPPLEO_ROOT_DIR && git --git-dir=$OPPLEO_ROOT_DIR/.git --work-tree=$OPPLEO_ROOT_DIR pull &> /dev/null)
  EXITCODE=$?
  if [ "$EXITCODE" == 0 ]; then
    printf " [${GREEN}${CHECKMARK}${NC}] Git pull succeeded ($EXITCODE) \n"
  else
    printf " [${RED}x${NC}] ${RED}Git pull failed! (exitcode $EXITCODE)${NC} \n"
  fi

  printf " [${GREEN}${CHECKMARK}${NC}] gitUpdate - Done \n"

  return $EXITCODE
}


function updateDatabase( ) {
  printf " [i] updateDatabase - Start \n"

  # Bash or Zsh?
  printf " [i] check shell type... \n"
  if [[ -f ~/.bashrc ]]; then
    printf " [${GREEN}${CHECKMARK}${NC}] Bash \n"
    printf " [i] get liquibase location from Bash... \n"
    lbpath=$(cat ~/.bashrc | grep liquibase | cut -d':' -f2)
  elif [[ -f ~/.zshrc ]]; then
    printf " [${GREEN}${CHECKMARK}${NC}] Zsh \n"
    printf " [i] get liquibase location from Zsh... \n"
    lbpath=$(cat ~/.zshrc | grep liquibase | cut -d':' -f2)
  else
    printf " [${RED}x${NC}] ${RED}Non-compatible shell used. Cannot determine liquibase location!${NC} (exitcode -8) \n"
    return -8
  fi
  printf " [i] liquibase at $lbpath \n"

  printf " [i] Release liquibase locks... \n"
  # (cd $OPPLEO_ROOT_DIR/db && liquibase releaseLocks &> /dev/null)
  (cd $OPPLEO_ROOT_DIR/db && $lbpath/liquibase releaseLocks &> /dev/null)
  EXITCODE=$?
  if [ "$EXITCODE" == 0 ]; then
    printf " [${GREEN}${CHECKMARK}${NC}] Success ($EXITCODE) \n"
  else
    printf " [${RED}x${NC}] ${RED}Failed to release locks!${NC} (exitcode $EXITCODE) \n"
  fi
  printf " [i] Run liquibase update... \n"
  # make sure the workling dir is changed. The parentheses spawn a subshell)
  # (cd $OPPLEO_ROOT_DIR/db && liquibase update &> /dev/null)
  (cd $OPPLEO_ROOT_DIR/db && $lbpath/liquibase update &> /dev/null)
  EXITCODE=$?
  if [ "$EXITCODE" == 0 ]; then
    printf " [${GREEN}${CHECKMARK}${NC}] Success ($EXITCODE) \n"
  else
    printf " [${RED}x${NC}] ${RED}Failed to run liquibase update!${NC} (exitcode $EXITCODE) \n"
  fi
 
  printf " [${GREEN}${CHECKMARK}${NC}] updateDatabase - Done \n"
}

# Cleanup
function cleanup() {
  printf " [i] cleanup - Start \n"

  # Deactivate the venv if it wasn't active at start
  # if [ $INVENV -ne 1 ]; then
  #   printf "  Deactivate active virtual environment ($VIRTUAL_ENV)... \n"
  #   deactivate
  # fi

  # go back to the original working dir
  # printf '  Changing back to original working directory...'
  # cd $CURRENT_WORKING_DIR

  printf " [${GREEN}${CHECKMARK}${NC}] cleanup - Done \n"
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


printf "Done! \n"
