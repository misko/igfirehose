sudo apt-get update
#sudo apt install -y git
sudo apt install -y python-pip
sudo pip install Scrapy
sudo pip install redis scrapy-useragents
#sudo apt install -y python-scrapy

#clone down the scrapy
git clone https://github.com/misko/instagram-scraper-1.git

 cd instagram-scraper-1/

#
#export h=dogsofinstagram
export h=catsofinstagram
#scrapy crawl -a redis_host=18.217.243.90 -a redis_password=bobsburgers -a hashtag=$h hashtag -a redis_port=6389
while [ 1 -lt 2 ]; do scrapy crawl -a redis_host=18.217.243.90 -a redis_password=bobsburgers -a hashtag=$h hashtag -a redis_port=6389; sleep 20; done

#CONFIG SET protected-mode no

#redus confifg
#requirepass bobsburgers
#protected-mode no
#port 6389
