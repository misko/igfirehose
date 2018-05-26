import redis
import json
import sys
import argparse

from IGFirehose import IGFirehose

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
