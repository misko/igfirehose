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
args = parser.parse_args()


igf = IGFirehose(args.config)
s=[]
breeds=args.breeds.split(',')
for breed in breeds:
	#p=igf.get_co_p(breed,args.tag,n=args.number)/(max(igf.get_co_p(breed,args.parent,n=args.number),0.01))
	n=igf.get_co_p(breed,args.parent,n=args.number)
	if n!=0:
		p=igf.get_co_p(breed,args.tag,n=args.number)/n
		#p=igf.get_co_p(args.tag,breed)
		if p!=0:
			#print "Pr(",breed,"|",args.tag,") / Pr(",breed,"|",args.parent,")=",p
			s.append((p,breed,n))
s.sort(reverse=True)
#print "Droppping",s[0]
#e_co_breed=sum([ x[0] for x in s[1:]])/float(len(s)-1)
#e_co_breed=sum([ x[0] for x in s[1:]])/sum( [ x[2] for x in s[1:]])
e_co_breed=sum([ x[0] for x in s[1:]])/sum( [ 1 for x in s[1:]])

isbreed=(1-e_co_breed) #*igf.get_co_p(args.parent,args.tag,n=args.number) 


print "isbreed=",isbreed
	
