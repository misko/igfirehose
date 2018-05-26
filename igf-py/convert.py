import redis
import json
import sys
import argparse
import zlib
from IGFirehose import IGFirehose
from random import shuffle

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
args = parser.parse_args()

igf = IGFirehose(args.config)
shortcodes = igf.shortcodes()
shortcodes = list(shortcodes)
shuffle(shortcodes)
for shortcode in shortcodes:
	edge=igf.get_shortcode(shortcode)


sys.exit(1)
imgs=igf.fetch_raw(args.tag,n=args.number)
for img in imgs:
	s=json.dumps(img)
	compressed =zlib.compress(s, 9)
	print len(s),len(compressed),float(len(compressed))/len(s)
	print img
	sys.exit(1)
	print compressed
sys.exit(1)
hashtag_counts={}
norm=0
for img in imgs:
	if len(img['hashtags'])>0:
		norm+=1
	for hashtag in img['hashtags']:
    		if hashtag not in hashtag_counts:
        		hashtag_counts[hashtag]=0
		hashtag_counts[hashtag]+=1


hashtags=[]
for k in hashtag_counts:
    frac=float(hashtag_counts[k])/norm
    if frac>0.001 and hashtag_counts[k]>2:
        hashtags.append((frac,k))
hashtags.sort(reverse=True)
#print hashtags
for f,hashtag in hashtags:
    for x in range(int(1000*f)):
        print hashtag.encode('utf-8').strip()
