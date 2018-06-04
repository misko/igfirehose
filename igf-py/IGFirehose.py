# encoding=utf8  
import sys

reload(sys)
sys.setdefaultencoding('utf8')
import math
import redis
import json
import zlib

#dash board

#tag 
#% scraped = total scraped / total images for tag

# word cloud or tags

# example images

#IGFirehose
#Connect / stats / fetch

lookup={
	'version':0,
	'hashtags':1,
	'url':2,
	'likes':3,
	'owner':4,
	'timestamp':5,
	'thumbnails':6,
	'shortcode':7
	}

class IGFirehose():
    def trim(self,edge):
    	new_edge={}
	if 'node' in edge:
		new_edge['caption']=""
		if len(edge['node']['edge_media_to_caption']['edges'])>0:
			new_edge['caption']=edge['node']['edge_media_to_caption']['edges'][0]['node']['text']
		new_edge['hashtags'] = self.string_to_hashtags(new_edge['caption'])
		new_edge['url'] = edge['node']['display_url']
		new_edge['likes'] = edge['node']['edge_liked_by']['count']
		new_edge['owner'] = edge['node']['owner']['id']
		new_edge['timestamp'] = int(edge['node']['taken_at_timestamp'])
		new_edge['thumbnails'] = edge['node']['thumbnail_resources'][:2]
		new_edge['shortcode'] = edge['node']['shortcode']
	else:
		new_edge=edge
	if 'version' not in new_edge:
		new_edge['version']=1
		thumbs=[]
		for idx in xrange(len(new_edge['thumbnails'])):
			thumbs.append(new_edge['thumbnails'][idx]['src'])
		new_edge['thumbnails']=thumbs
	edge_list=[None]*len(lookup)
	for field in lookup:
		edge_list[lookup[field]]=new_edge[field]
    	return edge_list
    
    def __init__(self,config_fn):
        self.config_fn=config_fn
        self.config={}
        self.read_config()
        self.redis_connect()

    def read_config(self):
        f=open(self.config_fn)
        for line in f:
            field=line.split()[0]
            value=line[len(field)+1:].strip()
            self.config[field]=value
            if field=='port':
                self.config[field]=int(self.config[field])
        f.close()

    def redis_connect(self):
        self.r = redis.Redis(
                host=self.config['redis-host'],
                port=self.config['redis-port'], 
                password=self.config['redis-password'])

    def get_mined_tags(self):
        return self.r.smembers('tags')

    def get_is_done(self,tag):
        return self.r.get('done_'+tag)

    def get_n_mined(self,tag):
	x=None
        if tag=='':
		x=self.r.scard('shortcodes')
	else:
        	x=self.r.scard('shortcodes_'+tag)
	if x==None:
		return 0
	return int(x)

    def get_n_tag(self,tag):
        sz=self.r.get('sizeof_'+tag)
	if not sz:
		return 0
	return int(sz)

    def string_to_hashtags(self,s):
        h=[]
        for x in s.split():
            if x[0]=='#' and len(x)>1:
                h.append(x.lower())
        return h

    def add_auto_tag(self,tag):
	 self.r.sadd("tags",tag)


    def str_to_edges(self,s):
        try:
            s = zlib.decompress(s)
        except:
            pass
	edge=json.loads(s)
	if isinstance(edge, list):
	    new_edge={}
	    for x in lookup:
		new_edge[x]=edge[lookup[x]]
            edge=new_edge
        return edge
        

    def fetch_raw(self,tag,n=200):
        shortcodes=self.r.srandmember("shortcodes_"+tag,-n)
        d=[]
        for shortcode in shortcodes:
            edge = self.r.get(shortcode)
            edge = self.str_to_edges(edge)
	    d.append(edge)
        return d
    
#    # pr ( tagA | tagB )
#    def get_co_p2(self,tagAs,tagB1,tagB2,n=1000):
#	if type(tagAs) is not list:
#		print "NEEDS TO BE LIST!"
#		sys.exit(1)
#        # get n posts from tagB
#	tagBs = [ tagB1.lower() , tagB2.lower() ]
#	
#	posts_raw = [ self.fetch(tagB1,keys=['hashtags'],n=n*10) , self.fetch(tagB2,keys=['hashtags'],n=n*10) ]
#	mine_from = 0 
#        posts=[]
#        for post in posts_raw[mine_from]:
#		if 
#		mine_from=1-mine_from
#	r={}
#	for tagA in tagAs:
#		r[tagA.lower()]=0
#	norm=0
#	for post in posts:
#		if ('#'+tagB) in post['hashtags']:
#			norm+=1
#			for tagA in tagAs:
#				tagA = tagA.lower()
#				#if len(post['hashtags'])>20:
#				#	continue
#				#norm+=len(post['hashtags'])
#				if ('#'+tagA) in post['hashtags']:
#				    r[tagA]+=1.0/len(post['hashtags'])
#		#r.append(hits/float(max(norm,1)))
#	return [ r[tagA.lower()]/float(norm) for tagA in tagAs ]
 
    # pr ( tagAs | posts )
    def get_co_p_from_posts(self,tagAs,tagBs,posts):
	if type(tagAs) is not list:
		print "NEEDS TO BE LIST!"
		sys.exit(1)
	if type(tagBs) is not list:
		print "NEEDS TO BE LIST!"
		sys.exit(1)
        # get n posts from tagB
	r={}
	for tagA in tagAs:
		r[tagA]=0
	norm=0
	for post in posts:
		post_has_all_tagBs=True
		for tagB in tagBs:
			if ('#'+tagB) not in post['hashtags']:
				post_has_all_tagBs=False
				break
		if not post_has_all_tagBs:
			continue
		norm+=1
		for tagA in tagAs:
			if ('#'+tagA) in post['hashtags']:
			    r[tagA]+=1.0/len(post['hashtags'])
	return [ r[tagA.lower()]/float(norm) for tagA in tagAs ]
       

    # pr ( tagA | tagB )
    def get_co_p(self,tagAs,tagB,n=1000):
	if type(tagAs) is not list:
		print "NEEDS TO BE LIST!"
		sys.exit(1)
        # get n posts from tagB
	tagB = tagB
	posts = self.fetch(tagB,keys=['hashtags'],n=n)
	r={}
	for tagA in tagAs:
		r[tagA]=0
	norm=0
	for post in posts:
		if ('#'+tagB) in post['hashtags']:
			norm+=1
			for tagA in tagAs:
				tagA = tagA.lower()
				#if len(post['hashtags'])>20:
				#	continue
				#norm+=len(post['hashtags'])
				if ('#'+tagA) in post['hashtags']:
				    r[tagA]+=1.0/len(post['hashtags'])
		#r.append(hits/float(max(norm,1)))
	return [ r[tagA.lower()]/float(norm) for tagA in tagAs ]

    def get_top_k_co_tags(self,tagA,k=50,n=1000):
        hits=0
        co_tags={}
        posts = self.fetch(tagA,keys=['hashtags'],n=n)
        for post in posts:
            for tag in post['hashtags']:
                if tag[1:]==tagA:
                    continue
                if tag not in co_tags:
                    co_tags[tag]=0
                #co_tags[tag]+=1
                co_tags[tag]+=1.0/len(post['hashtags'])
        #lets sort and return
        l=[]
        for tag in co_tags:
            l.append((co_tags[tag],tag))
        l.sort(reverse=True)
        return [ x[1][1:] for x in l[:k] ]
   
 
    #THIS IS NOT KL....
    def get_sim(self,tagA,tagB,k=50,n=1000):
        s=0
        tags_used=0
        top_k=self.get_top_k_co_tags(tagA,k+1,n)
        p_i=self.get_co_p(top_k,tagA,n)
        q_i=self.get_co_p(top_k,tagB,n)
        for idx in xrange(len(top_k)):
            tagZ=top_k[idx]
            if tagZ==tagB:
                continue
            if q_i[idx]!=0:
		if p_i[idx]>0:
                	s+=p_i[idx]*min(10,math.log(p_i[idx]/q_i[idx]))
            else:
                s+=10*p_i[idx]
            tags_used+=1
            if tags_used>=k:
                break
        return s

    def fetch2(self,tagA,tagB,n=200,keys=('hashtags','url','likes','owner','timestamp','thumbnails','shortcode')):
        assert(n>0)
        posts=[]
        while len(posts)<n:
            posts_gs = [ self.fetch(tagA,n=n,keys=keys) , self.fetch(tagB,n=n,keys=keys) ]
            for posts_g in posts_gs:
            	for post in posts_g:
                    if ('#'+tagA) in post['hashtags'] and ('#'+tagB) in post['hashtags']:
                        posts.append(post)
        return posts

    def fetch(self,tag,n=200,keys=('hashtags','url','likes','owner','timestamp','thumbnails','shortcode')):
        #granb
	shortcodes=None
	if n>=0:
            shortcodes=self.r.srandmember("shortcodes_"+tag,-n)
        else:
            shortcodes=self.r.smembers("shortcodes_"+tag)
        #d=[]
        for shortcode in shortcodes:
	    edge = self.get_shortcode(shortcode)
	    trimmed_edge = {}
            for key in keys:
                trimmed_edge[key]=edge[key]
            yield edge
            #d.append(edge)
        #return d

    def shortcodes(self,n=0):
	if n>0:
		return self.r.srandmember('shortcodes',-n)
        return self.r.smembers('shortcodes')

    def get_shortcode(self,shortcode):
        edge_str = self.r.get(shortcode)
        if edge_str[0]=='{': #this may be old shortcode
		try:
			edge=json.loads(edge_str)
			edge=self.trim(edge)
        		edge_str = zlib.compress(json.dumps(edge), 9)
        		self.r.set(shortcode,edge_str)
		except:
			pass
	edge=self.str_to_edges(edge_str)
	if 'version' not in edge:
		edge=self.trim(edge)
        	edge_str = zlib.compress(json.dumps(edge), 9)
        	self.r.set(shortcode,edge_str)
	edge=self.str_to_edges(edge_str)
        return edge




