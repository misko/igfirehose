import redis
import sys
import string
import random
import time
#https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_tag_auto(r,seconds):
    for x in xrange(6):
        tag=r.srandmember('tags',-1)
        if tag:
            tag=tag[0]
            mining_tag='mining_'+tag
            current_value=r.get(mining_tag)
            if current_value==None:
                pipe=r.pipeline(True)
                pipe.watch(mining_tag)
                current_value=r.get(mining_tag)
                rid=id_generator()
                if current_value!=None:
                    pipe.unwatch()
                else:
                    try:
                        pipe.multi()
                        pipe.set(mining_tag,rid)
                        pipe.expire(mining_tag,seconds)
                        if pipe.execute():
                            return tag,rid
                    except redis.exceptions.WatchError:
                        pass
        print "Failed to get an auto tag! Sleep then try!"
    return None,None

def refresh_auto_tag(r,tag,rid,seconds):
    mining_tag='mining_'+tag
    current_value=r.get(mining_tag)
    if current_value==rid:
        pipe=r.pipeline(True)
        pipe.watch(mining_tag)
        current_value=r.get(mining_tag)
        if current_value!=rid:
            pipe.unwatch()
        else:
            try:
                pipe.multi()
                pipe.set(mining_tag,rid)
                pipe.expire(mining_tag,seconds)
                if pipe.execute():
                    return True
            except redis.exceptions.WatchError:
                pass
    return False

if __name__=='__main__':
    if len(sys.argv)!=4:
        print "% ip port password"
        sys.exit(1)

    ip=sys.argv[1]
    port=int(sys.argv[2])
    password=sys.argv[3]

    r = redis.Redis(
        host=ip,
        port=port,
        password=password)
    #get an auto tag
    tag,rid=get_tag_auto(r,600)
    #sleep for a bit
    print r.ttl("mining_"+tag)
    print refresh_auto_tag(r,tag,rid,900)
    print r.ttl("mining_"+tag)
