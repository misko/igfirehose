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
parser.add_argument("-c","--config", help="config file",required=True,type=str)
parser.add_argument("-m","--norm", help="norm",action="store_true")
args = parser.parse_args()



m={}

igf = IGFirehose(args.config)
tags = args.tags.split(',')


for tag in tags:
	p=igf.get_co_p(tags,tag,n=args.number)
	m[tag]={}
	for x in xrange(len(tags)):
		m[tag][tags[x]]=p[x]

#print headers
print "PR(A | B )"
r=['B \ A']
for xA in xrange(len(tags)):
	r.append(tags[xA])
print ",".join(r)
	
for xA in xrange(len(tags)): #rows
	tagA=tags[xA]
	r=[tagA]
	for xB in xrange(len(tags)):
		tagB=tags[xB]
		if args.norm:
			r.append("%0.3e" % (m[tagA][tagB]/(m[tagA][tagB]+m[tagB][tagA])))
		else:
			r.append("%0.3e" % m[tagA][tagB])
	print ",".join(r)
