# IGFirehose

## Mining

### Server worker model

To mine images from instagram there is a server / worker model where the server contains a redis database of posts that have been mined, urls for the images (but not the images themselves) and resume points to continue mining for each tag. The clients then connect to the server request a tag to mine, parse results and submit them to the redis database, until they get blocked by IG, then they wait while another available worker can connect to the server and continue mining where the first one (that was blocked) left off.

### Server setup

* Create pip enviornment
* Install , configure and bring up redis
* Create a client configuration file
* Add tags to be auto-mined
* Start web front end

### Server quick start
```
git clone --recurse-submodules https://github.com/misko/igfirehose.git
cd igfirehose
virtualenv env
source env/bin/activate
pip install -r requirements.txt
redis-server &
sleep 1
redis-cli config set requirepass bobsburgers
cd igf-py
python www.py
```


### Client setup

* Create pip enviornment
* Run the crawler, 
scrapy crawl -a config_fn=igf-py/igf.conf -a n=100000 -a hashtag="" hashtag

With hashtag="" you must add tags to mine in igf-py/add_tag_auto.py .  That way it will show up in the served webpage as well.  To see what hashtags have been added to be automatically mined, use igf-py/query_tags.py -c <your_config_file>

## Client quick start
```
git clone --recurse-submodules https://github.com/misko/igfirehose.git
cd igfirehose
virtualenv env
source env/bin/activate
pip install -r requirements.txt
crapy crawl -a config_fn=igf-py/igf.conf -a n=100000 -a hashtag="" hashtag
```

To add a word cloud of associated tags, go to scripts and run make_all_word_clouds.sh .  The resulting world cloud can be accessed on the webpage. 

To download images whose url were scrapped. Use: 
```
while [ 1 -lt 2 ]; do python3 query_urls.py -t makeup -n 1000 -c igf.conf | while read line; do dest_fn=downloads/`basename $line`; dest_fn=`echo ${dest_fn} | tr "?" " " | awk '{print $1}'`; echo ${dest_fn};  if [ ! -f ${dest_fn} ]; then wget "$line"  -O ${dest_fn} 2> /dev/null; fi; done; sleep 5s; done

```
Where you created a downloads/ folder to store the downloaded images. 
