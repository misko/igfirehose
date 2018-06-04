# encoding=utf8  
import sys

reload(sys)
sys.setdefaultencoding('utf8')
import redis
import json
import argparse
import zlib
from IGFirehose import IGFirehose

parser = argparse.ArgumentParser(
prog='PROG',
description='''query IGFirehose - Pr( tagA | tag B )''')
parser.add_argument("-a","--tagA", help="hashtag",type=str,required=True)
parser.add_argument("-b","--tagBs", help="hashtag",type=str,required=True)
parser.add_argument("-n","--number", help="hashtag",type=int, default=10000)
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
args = parser.parse_args()

tagBs=args.tagBs.split(',')
assert(len(tagBs)==2)

igf = IGFirehose(args.config)
posts=igf.fetch2(tagBs[0],tagBs[1],n=args.number,keys=['hashtags'])
print "GOT THE POSTS"
print igf.get_co_p_from_posts([args.tagA],tagBs,posts)
