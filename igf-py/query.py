import redis
import json
import sys
import argparse

#dash board

#tag 
#% scraped = total scraped / total images for tag

# word cloud or tags

# example images

#IGFirehose
#Connect / stats / fetch

class IGFirehose():
    def __init__(self,config_fn):
        self.config_fn=config_fn
        self.config={}
        self.read_config()
        self.redis_connect()

    def read_config(self):
        f=open(self.config_fn)
        for line in f:
            field=line.split()[0]
            value=line[len(field)+1:].strip()
            self.config[field]=value
            if field=='port':
                self.config[field]=int(self.config[field])
        f.close()

    def redis_connect(self):
        self.r = redis.Redis(
                host=self.config['redis-host'],
                port=self.config['redis-port'], 
                password=self.config['redis-password'])

    def get_mined_tags(self):
        return self.r.smembers('tags')

    def string_to_hashtags(self,s):
        h=[]
        for x in s.split():
            if x[0]=='#' and len(x)>1:
                h.append(x)
        return h

    def fetch(self,tag,n=200,keys=('hashtags','url','likes','owner','timestamp')):
        #granb
        shortcodes=self.r.srandmember("shortcodes_"+tag,-n)
        d=[]
        for shortcode in shortcodes:
            edge = self.r.get(shortcode)
            edge = json.loads(edge) 
            caption = ""
            current = {}
            if len(edge['node']['edge_media_to_caption']['edges'])>0:
                caption=edge['node']['edge_media_to_caption']['edges'][0]['node']['text']
            if 'hashtags' in keys:
                current['hashtags'] = self.string_to_hashtags(caption)
            if 'url' in keys:
                current['url'] = edge['node']['display_url']
            if 'likes' in keys:
                current['likes'] = edge['node']['edge_liked_by']['count']
            if 'owner' in keys:
                current['owner'] = edge['node']['owner']['id']
            if 'timestamp' in keys:
                current['timestamp'] = int(edge['node']['taken_at_timestamp'])
            d.append(current)
        return d


parser = argparse.ArgumentParser()
parser.add_argument("-t","--tag", help="hashtag",type=str)
parser.add_argument("-m","--mode", help="stats/fetch",type=str)
parser.add_argument("-n","--number", help="how many",type=int)
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
args = parser.parse_args()


igf = IGFirehose(args.config)
print igf.fetch('dogsofinstagram',n=args.number)
sys.exit(1)



for hashtag in hashtags:
    if hashtag not in hashtag_counts:
        hashtag_counts[hashtag]=0
    hashtag_counts[hashtag]+=1


hashtags=[]
for k in hashtag_counts:
    frac=float(hashtag_counts[k])/n
    if frac>0.001 and hashtag_counts[k]>2:
        hashtags.append((frac,k))
hashtags.sort(reverse=True)
#print hashtags
for f,hashtag in hashtags:
    for x in range(int(100*f)):
        print hashtag
