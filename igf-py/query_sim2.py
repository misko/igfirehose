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



m={}
def memo(tagA,tagB):
	k=tagA+"|"+tagB
	if k not in m:
		m[k]=igf.get_sim(tagA,tagB,n=args.number)
	return m[k]

igf = IGFirehose(args.config)
tags = args.tags.split(',')

#print headers
r=['X']
for xA in xrange(len(tags)):
	r.append(tags[xA])
print ",".join(r)
	
for xA in xrange(len(tags)): #rows
	tagA=tags[xA]
	r=[tagA]
	for xB in xrange(len(tags)):
		tagB=tags[xB]
                fwd=memo(tagA,tagB)
		#bwd=memo(tagB,tagA)
		#print tagA,tagB,max(fwd,bwd),min(fwd,bwd),(fwd+bwd)/2,fwd,bwd
		r.append("%0.3f" % fwd)
	print ",".join(r)
