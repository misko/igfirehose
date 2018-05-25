import redis
import json
import sys

if len(sys.argv)!=6:
    print "%s ip port password tag n" % sys.argv[0]
    sys.exit(1)

ip=sys.argv[1]
port=int(sys.argv[2])
password=sys.argv[3]
tag=sys.argv[4]
n=int(sys.argv[5])

r = redis.Redis(
    host=ip,
    port=port, 
    password=password)

def get_hashtags(s):
    h=[]
    for x in s.split():
        if x[0]=='#' and len(x)>1:
            h.append(x)
    return h

hashtag_counts={}

#shortcodes=r.smembers("shortcodes_"+tag)
shortcodes=r.srandmember("shortcodes_"+tag,-n)
for shortcode in shortcodes:
    edge = r.get(shortcode)
    edge = json.loads(edge) 
    #print edge['node']['display_url']
    #print edge
    caption = ""
    if len(edge['node']['edge_media_to_caption']['edges'])>0:
        caption=edge['node']['edge_media_to_caption']['edges'][0]['node']['text']
    hashtags = get_hashtags(caption)
    #print "HASH",hashtags
    for hashtag in hashtags:
        if hashtag not in hashtag_counts:
            hashtag_counts[hashtag]=0
        hashtag_counts[hashtag]+=1
    #print "*"*80


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
