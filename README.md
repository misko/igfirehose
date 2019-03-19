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

### Client setup

* Create pip enviornment
* Run the crawler, scrapy crawl -a config_fn=igf.conf -n 10000000 hashtag

