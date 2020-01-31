# Reaspberry config
echo "Install script for the CarChargerWebApp service"
echo "v0.2 31-01-2020"
echo " determining the location of the install script..."
# DIR holds the directory of webapp
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo " install script in dir $DIR..."
# PRJDIR holds the root directory of rhe project
PRJDIR=${DIR%"/webapp"}
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
    echo '/proc/cpuinfo exist'
    if grep -q 'Raspberry' /proc/cpuinfo; then
        echo 'found'
        raspberry=true
    fi
fi
if [ "$raspberry" = true ]; then
    echo " On a raspberry :)"
    echo " - installing raspberry dependencies incl mfrc522, RPi.GPIO, and spidev..."
    pip install -r $PRJDIR/requirements_raspberry.txt > /dev/null 2>&1
    echo " - preparing service file CarChargerWebApp.service from template by updating path..."
    sed 's?#WORKINGDIR_PLACEHOLDER?'$PRJDIR'?'g < $DIR/CarChargerWebApp.service.template >$DIR/CarChargerWebApp.service
    echo " - stopping CarChargerWebApp if running..."
    sudo systemctl stop CarChargerWebApp
    echo " - Update config/ installing CarChargerWebApp.service for systemd..."
    sudo cp $DIR/CarChargerWebApp.service /etc/systemd/system/CarChargerWebApp.service
    echo " - reloading daemon config..."
    sudo systemctl daemon-reload
    echo " - starting CarChargerWebApp systemd daemon..."
    sudo systemctl start CarChargerWebApp
    sudo systemctl status CarChargerWebApp
else
    echo " Not on a raspberry..."
    echo " - installing dependencies without mfrc522, RPi.GPIO, and spidev..."
    pip install -r $PRJDIR/requirements_non_raspberry.txt > /dev/null 2>&1
    echo " - not installing the service."
fi
echo "Done!"
