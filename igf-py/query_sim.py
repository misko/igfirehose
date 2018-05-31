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
parser.add_argument("-t","--tags", help="hashtag",type=str,required=True)
parser.add_argument("-n","--number", help="hashtag",type=int, default=1000)
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
args = parser.parse_args()

igf = IGFirehose(args.config)
tags = args.tags.split(',')
for tagA in tags:
	for tagB in tags:
                fwd=igf.get_sim(tagA,tagB,n=args.number)
		bwd=igf.get_sim(tagB,tagA,n=args.number)
		print tagA,tagB,max(fwd,bwd),fwd,bwd
