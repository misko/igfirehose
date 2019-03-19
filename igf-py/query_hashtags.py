import redis
import json
import sys
import argparse

from IGFirehose import IGFirehose

parser = argparse.ArgumentParser()
parser.add_argument("-t","--tag", help="hashtag",type=str,required=True)
parser.add_argument("-n","--number", help="number of images",type=int, default=200)
parser.add_argument("-m","--mode", help="stats/fetch",type=str)
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
args = parser.parse_args()

igf = IGFirehose(args.config)
imgs=igf.fetch(args.tag,n=args.number,keys=('hashtags',))

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
        print(hashtag.strip())
