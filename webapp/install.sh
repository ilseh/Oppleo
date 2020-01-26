# Reaspberry config
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
