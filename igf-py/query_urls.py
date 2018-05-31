import redis
import json
import sys
import argparse

from IGFirehose import IGFirehose

parser = argparse.ArgumentParser()
parser.add_argument("-t","--tag", help="hashtag",type=str,required=True)
parser.add_argument("-n","--number", help="number of images",type=int, default=200)
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
args = parser.parse_args()

igf = IGFirehose(args.config)

for img in igf.fetch(args.tag,n=args.number,keys=('url',)):
	#print u' '.join(img['hashtags']).encode('utf-8').strip()
	print img['url']
