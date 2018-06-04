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
description='''query IGFirehose = 1 - avg( cotag( b | t ) )/N , b in breeds''')
parser.add_argument("-t","--tag", help="hashtag",type=str,required=True)
parser.add_argument("-b","--breeds", help="breeds",type=str,default="bulldog,husky,mastiff,greatdane,chihuahua,beagle,pomeranian,stbernard,cockerspaniel,dalmatian,greyhound")
#parser.add_argument("-x","--not-breeds", help="breeds",type=str,default="dogs,puppies,love")
parser.add_argument("-n","--number", help="hashtag",type=int, default=5000)
parser.add_argument("-p","--parent", help="hashtag",type=str,default="dogsofinstagram")
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
parser.add_argument("-v","--verbose", help="increase output verbosity",action="store_true")
args = parser.parse_args()


breeds=args.breeds.split(',')
igf = IGFirehose(args.config)
ns=igf.get_co_p(breeds,args.parent,n=args.number)
ps=igf.get_co_p(breeds,args.tag,n=args.number)
s=[]
for x in xrange(len(breeds)):
	breed=breeds[x]
	#p=igf.get_co_p(breed,args.tag,n=args.number)/(max(igf.get_co_p(breed,args.parent,n=args.number),0.01))
	#n=igf.get_co_p(breed,args.parent,n=args.number)
	n=ns[x]
	if n!=0:
		#p=igf.get_co_p(breed,args.tag,n=args.number)
		p=ps[x]
		#p=igf.get_co_p(args.tag,breed)
		if p!=0:
			if args.verbose:
				print "Pr(",breed,"|",args.tag,") / Pr(",breed,"|",args.parent,")=",p/n,p,n
			s.append((min(1.0,p/n),breed,n))
s.sort(reverse=True)
#print "Droppping",s[0]
#e_co_breed=sum([ x[0] for x in s[1:]])/float(len(s)-1)
#e_co_breed=sum([ x[0] for x in s[1:]])/sum( [ x[2] for x in s[1:]])
e_co_breed=sum([ x[0] for x in s[1:]])/sum( [ 1 for x in s[1:]])

isbreed=(1-e_co_breed) #*igf.get_co_p(args.parent,args.tag,n=args.number) 


print "isbreed=",isbreed
	
