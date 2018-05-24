import redis
import json
import sys

if len(sys.argv)!=6:
    print "%s ip port password tag n" % sys.argv[0]
    sys.exit(1)

ip=sys.argv[1]
port=int(sys.argv[2])
password=sys.argv[3]
tag=sys.argv[4]
n=int(sys.argv[5])

r = redis.Redis(
    host=ip,
    port=port, 
    password=password)

#shortcodes=r.smembers("shortcodes_"+tag)
shortcodes=r.srandmember("shortcodes_"+tag,-n)
for shortcode in shortcodes:
    edge = r.get(shortcode)
    print edge
    print ""
    edge=edge.replace("'",'+|X').replace('"',"'").replace('+|X','"')
    print edge
    edge=edge.replace('{u"','{"').replace(' u"',' "').replace('False','0').replace('True','1')
    print edge
    #print eval(edge.replace("'","\\'").replace('\n',''))
    parsed_json = json.loads(edge.replace("'",'"'))
    print parsed_json
