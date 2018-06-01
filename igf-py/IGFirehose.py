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
    
    # pr ( tagA | tagB )
    def get_co_p(self,tagA,tagB,n=1000):
        # get n posts from tagB
        tagA = tagA.lower()
        tagB = tagB.lower()
        posts = self.fetch(tagB,keys=['hashtags'],n=n)
        hits=0
        norm=0
        for post in posts:
            if ('#'+tagB) in post['hashtags']:
                #norm+=1
		#if len(post['hashtags'])>20:
		#	continue
                norm+=len(post['hashtags'])
                if ('#'+tagA) in post['hashtags']:
                    hits+=1
                    continue
        return hits/float(max(norm,1))

    def get_top_k_co_tags(self,tagA,k=10,n=1000):
        hits=0
        co_tags={}
        posts = self.fetch(tagA,keys=['hashtags'],n=n)
        for post in posts:
            hashtags=map( lambda  x : x.lower() , post['hashtags'] )
            for tag in hashtags:
                if tag[1:]==tagA:
                    continue
                if tag not in co_tags:
                    co_tags[tag]=0
                co_tags[tag]+=1
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
        for tagZ in self.get_top_k_co_tags(tagA,k+1,n):
            if tagZ==tagB:
                continue
            p_i=self.get_co_p(tagZ,tagA,n)
            q_i=self.get_co_p(tagZ,tagB,n)
            if q_i!=0:
                s+=p_i*min(10,math.log(p_i/q_i))
            else:
                s+=10*p_i
            tags_used+=1
            if tags_used>=k:
                break
        return s


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




