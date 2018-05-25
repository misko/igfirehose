sudo apt-get update
sudo apt-get install -y nginx
sudo rm /etc/nginx/nginx.conf
sudo ln -s /ig/www/nginx.conf /etc/nginx/
sudo systemctl restart nginx
