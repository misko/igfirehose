import redis

import sys

if len(sys.argv)!=5:
    print "%s ip port password tag_to_remove" % sys.argv[0]
    sys.exit(1)

ip=sys.argv[1]
port=int(sys.argv[2])
password=sys.argv[3]
tag=sys.argv[4]

r = redis.Redis(
    host=ip,
    port=port, 
    password=password)
print r.get("resume_"+tag)
