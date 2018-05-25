import redis
import sys

if len(sys.argv)!=5:
    print "% ip port password tag"
    sys.exit(1)

ip=sys.argv[1]
port=int(sys.argv[2])
password=sys.argv[3]
tag=sys.argv[4].strip()
if len(tag)==0:
    sys.exit(1)
r = redis.Redis(
    host=ip,
    port=port,
    password=password)

print r.sadd("tags",tag)
#print r.delete("mining_"+tag)
