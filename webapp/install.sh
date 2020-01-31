# Reaspberry config
echo "Install script for the CarChargerWebApp service"
echo " v0.2 31-01-2020"
echo " determining the location of the install script..."
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo " install script in dir $DIR..."
PRJDIR=${DIR%"/webapp"}
echo " project root $PRJDIR..."
echo " preparing service file CarChargerWebApp.service from template by updating path..."
# sed 's?#WORKINGDIR_PLACEHOLDER?'`pwd`'?' < $DIR/CarChargerWebApp.service.template >$DIR/CarChargerWebApp.service
sed 's?#WORKINGDIR_PLACEHOLDER?'$PRJDIR'?' < $DIR/CarChargerWebApp.service.template >$DIR/CarChargerWebApp.service
echo "Stopping CarChargerWebApp if running..."
sudo systemctl stop CarChargerWebApp
echo "Update config/ installing CarChargerWebApp.service for systemd..."
sudo cp CarChargerWebApp.service /etc/systemd/system/CarChargerWebApp.service
echo "Reloading daemon config..."
sudo systemctl daemon-reload
echo "Starting CarChargerWebApp systemd daemon..."
sudo systemctl start CarChargerWebApp
sudo systemctl status CarChargerWebApp
echo "Done!"
