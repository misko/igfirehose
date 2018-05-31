import redis
import json
import sys
import argparse
import zlib
from IGFirehose import IGFirehose

parser = argparse.ArgumentParser()
parser.add_argument("-r","--roots", help="root tags",type=str,default="dogsofinstagram,catsofinstagram")
parser.add_argument("-n","--number", help="min number of images per tag",type=int, default=800)
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
args = parser.parse_args()

igf = IGFirehose(args.config)

hashtag_counts={}
for img in igf.fetch(args.tag,n=args.number,keys=('hashtags',)):
	print u' '.join(img['hashtags']).encode('utf-8').strip()
	for hashtag in img['hashtags']:
		hashtag=hashtag.encode('utf-8').strip()    
    		if hashtag not in hashtag_counts:
        		hashtag_counts[hashtag]=0
		hashtag_counts[hashtag]+=1

hashtags=[]
for k in hashtag_counts:
    frac=float(hashtag_counts[k])/norm
    if frac>0.0001 and hashtag_counts[k]>1:
        hashtags.append((frac,k))
hashtags.sort(reverse=True)
#print hashtags
for f,hashtag in hashtags:
    for x in range(int(1000*f)):
        print hashtag.encode('utf-8').strip()
