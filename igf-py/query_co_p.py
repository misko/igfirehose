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
parser.add_argument("-b","--tagB", help="hashtag",type=str,required=True)
parser.add_argument("-n","--number", help="hashtag",type=int, default=10000)
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
args = parser.parse_args()

igf = IGFirehose(args.config)
print igf.get_co_p(args.tagA,args.tagB,n=args.number)
