# -*- coding: utf-8 -*-
# encoding=utf8  
import sys  

#reload(sys)  
#sys.setdefaultencoding('utf8')
import scrapy
import json
import time
import os.path
import json
from scrapy.exceptions import CloseSpider
from scrapy_instagram import schedule
from scrapy_instagram.items import Post
import zlib
import redis


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

def string_to_hashtags(s):
	h=[]
	for x in s.split():
		if x[0]=='#' and len(x)>1:
			h.append(x.lower())
	return h
def trim(edge):
	new_edge={}
	if 'node' in edge:
		new_edge['caption']=""
		if len(edge['node']['edge_media_to_caption']['edges'])>0:
			new_edge['caption']=edge['node']['edge_media_to_caption']['edges'][0]['node']['text']
		new_edge['hashtags'] = string_to_hashtags(new_edge['caption'])
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
		for idx in range(len(new_edge['thumbnails'])):
			thumbs.append(new_edge['thumbnails'][idx]['src'])
		new_edge['thumbnails']=thumbs
	edge_list=[None]*len(lookup)
	for field in lookup:
		edge_list[lookup[field]]=new_edge[field]
	return edge_list

class InstagramSpider(scrapy.Spider):
	name = "hashtag"  # Name of the Spider, required value
	custom_settings = {
		'FEED_URI': './scraped/%(name)s/%(hashtag)s/%(time)s',
	}
	checkpoint_path = './scraped/%(name)s/%(hashtag)s/.checkpoint'
	handle_httpstatus_list = [404,429]

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

	#def __init__(self, hashtag='',config_fn="",n=""):
	def __init__(self, *args, **kwargs):
		self.config={}
		self.config_fn=kwargs['config_fn']
		self.read_config()
		self.hashtag=kwargs['hashtag']
		self.reset()
		self.auto_tag=False
		self.rid=None
		self.n=int(kwargs['n'])

	def reset(self):
		self.redis_connect()
		if self.hashtag == '':
			self.hashtag,self.rid=schedule.get_tag_auto(self.r,60)
			self.auto_tag=True
			if self.hashtag==None:
				print("FAIL: Failed to get a hastag to mine")
				raise CloseSpider('FAIL: Failed to get a hastag to mine')
		resume=self.r.get("resume_"+self.hashtag)
		if resume:
			self.start_urls = [resume.decode('utf-8')]
		else:
			self.start_urls = ["https://www.instagram.com/explore/tags/"+self.hashtag+"/?__a=1"]
		self.r.set("resume_"+self.hashtag, self.start_urls[-1])

		self.count=0
		self.punt=0
		self.start=int(time.time())


	# Entry point for the spider
	def parse(self, response):
		return self.parse_htag(response)

	# Method for parsing a hastag
	def parse_htag(self, response):
		if response.status == 404:
			#got 404 , reset tag?
			print("404,reset tag?")
		if response.status == 429:
			if self.rid!=None: 
					schedule.rm_auto_tag(self.r,self.hashtag)
			time.sleep(20)
			raise CloseSpider('FAIL: All out of love, and so lost without you')
		print(self.r.ttl('mining_'+self.hashtag))
		print("AGENT",response.request.headers['User-Agent'] )
		#Load it as a json object
		graphql = json.loads(response.text)
		has_next = graphql['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
		edges = graphql['graphql']['hashtag']['edge_hashtag_to_media']['edges']
		try:
			total = int(graphql['graphql']['hashtag']['edge_hashtag_to_media']['count'])
			self.r.set('sizeof_'+self.hashtag,total)
		except:
			pass

		#if not hasattr(self, 'starting_shorcode') and len(edges):
		#	self.starting_shorcode = edges[0]['node']['shortcode']
		#	filename = self.checkpoint_path
		#	f = open(filename, 'w')
		#	f.write(self.starting_shorcode)

		for edge in edges:
			node = edge['node']
			if self.r.sismember('shortcodes',node['shortcode'])==0:
				self.count+=1
			else:
				self.punt+=1
			trimmed_edge=trim(edge)
			compressed_edge=zlib.compress(json.dumps(trimmed_edge).encode('utf-8'), 9)
			self.r.set(node['shortcode'], compressed_edge)
			self.r.sadd('shortcodes',node['shortcode'])
			self.r.sadd('shortcodes_'+self.hashtag,node['shortcode'])
			#print edge
			#print "XXX",edge
			#shortcode = node['shortcode']
			#if(self.checkAlreadyScraped(shortcode)):
			#	return
			#yield scrapy.Request("https://www.instagram.com/p/"+shortcode+"/?__a=1", callback=self.parse_post)
		now=int(time.time())
		sz=self.r.scard('shortcodes_'+self.hashtag)
		if self.n>0 and sz>self.n:
			print("DONE SCRAPING")
			raise CloseSpider('DONE: MY WORK IS DONE!')
		print("SPEED",self.count/(float(now-self.start)+1),"NEW",self.count,"PUNT",self.punt,"TOTAL",sz)

		if has_next:
			end_cursor = graphql['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
			self.r.set("resume_"+self.hashtag, "https://www.instagram.com/explore/tags/"+self.hashtag+"/?__a=1&max_id="+end_cursor)
			#hits_per_hour=200.0
			#seconds_per_hit=(60.0*60.0)/hits_per_hour
			#time.sleep(seconds_per_hit)
			if self.auto_tag and self.r.ttl('mining_'+self.hashtag)<180:
				schedule.refresh_auto_tag(self.r,self.hashtag,self.rid,1200)
			yield scrapy.Request("https://www.instagram.com/explore/tags/"+self.hashtag+"/?__a=1&max_id="+end_cursor, callback=self.parse_htag)
		else:
			self.r.set('done_'+self.hashtag,time.time())
		   
	def parse_post(self, response):
		graphql = json.loads(response.text)
		media = graphql['graphql']['shortcode_media']
		location = media.get('location', {})
		if location is not None:
			loc_id = location.get('id', 0)
			request = scrapy.Request("https://www.instagram.com/explore/locations/"+loc_id+"/?__a=1", callback=self.parse_post_location, dont_filter=True)
			request.meta['media'] = media
			yield request
		else:
			media['location'] = {}
			yield self.makePost(media)		 

	def parse_post_location(self, response):
		media = response.meta['media']
		location = json.loads(response.text)
		location = location['location']
		media['location'] = location
		yield self.makePost(media)

	def makePost(self, media):
		location = media['location']
		caption = ''
		if len(media['edge_media_to_caption']['edges']):
			caption = media['edge_media_to_caption']['edges'][0]['node']['text']
		return Post(id=media['id'],
					shortcode=media['shortcode'],
					caption=caption,
					display_url=media['display_url'],
					loc_id=location.get('id', 0),
					loc_name=location.get('name',''),
					loc_lat=location.get('lat',0),
					loc_lon=location.get('lng',0),
					owner_id =media['owner']['id'],
					owner_name = media['owner']['username'],
					taken_at_timestamp= media['taken_at_timestamp'])
