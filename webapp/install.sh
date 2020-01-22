# Reaspberry config
echo "uWSGI"
echo "...stopping uWSGI..."
sudo systemctl stop CarChargerWebApp
echo "...installing CarChargerWebApp.service for uWSGI"
sudo cp CarChargerWebApp.service /etc/systemd/system/CarChargerWebApp.service
echo "...deleting uwsgi directory in /var/run"
sudo rm -rf /var/run/uwsgi
echo "...creating uwsgi directory in /var/run for sock file"
sudo mkdir /var/run/uwsgi
sudo chmod 777 /var/run/uwsgi
sudo chown pi:pi /var/run/uwsgi
echo "...creating socket file in /var/run"
touch /var/run/uwsgi/CarChargerWebApp.sock
echo "...for now chmod 777 on the sock file"
chown pi:pi /var/run/uwsgi/CarChargerWebApp.sock
chmod 777 /var/run/uwsgi/CarChargerWebApp.sock
echo "...reloading daemon config"
sudo systemctl daemon-reload
echo "...starting CarChargerWebApp uWSGI daemon"
sudo systemctl start CarChargerWebApp
sudo systemctl status CarChargerWebApp
echo "NGINX"
RND="$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c20)"
echo "...moving current default nginx config from default to default.${RND}"
sudo mv /etc/nginx/sites-available/default /etc/nginx/sites-available/default.${RND}
echo "...installing CarChargerWebApp as default available nginx website"
sudo cp CarChargerWebApp /etc/nginx/sites-available/default
echo "...set CarChargerWebApp as default active website" 
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
echo "...Testing config..."
sudo nginx -t
echo "...restarting nginx"
sudo systemctl restart nginx
sudo systemctl status nginx
