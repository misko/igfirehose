# -*- coding: utf-8 -*-
import scrapy
import json
import time
import os.path
import json
from scrapy.exceptions import CloseSpider

from scrapy_instagram.items import Post


import redis


class InstagramSpider(scrapy.Spider):
    name = "hashtag"  # Name of the Spider, required value
    custom_settings = {
        'FEED_URI': './scraped/%(name)s/%(hashtag)s/%(date)s',
    }
    checkpoint_path = './scraped/%(name)s/%(hashtag)s/.checkpoint'
    handle_httpstatus_list = [404]

    # def closed(self, reason):
    #     self.logger.info('Total Elements %s', response.url)

    def __init__(self, hashtag='',redis_host='',redis_password='',redis_port=0):
        redis_port=int(redis_port)
        print redis_host,redis_password,"XX"
        self.r = redis.Redis(
            host=redis_host,password=redis_password,port=redis_port)
        self.hashtag = hashtag
        if hashtag == '':
            self.hashtag = input("Name of the hashtag? ")
        resume=self.r.get("resume_"+self.hashtag)
        if resume:
            self.start_urls = [resume]
        else:
            self.start_urls = ["https://www.instagram.com/explore/tags/"+self.hashtag+"/?__a=1"]
        self.r.set("resume_"+self.hashtag, self.start_urls[-1])

        self.date = time.strftime("%d-%m-%Y_%H")
        self.checkpoint_path = './scraped/%s/%s/.checkpoint' % (self.name, self.hashtag)
        self.count=0
        self.punt=0
        self.start=int(time.time())

    # Entry point for the spider
    def parse(self, response):
        if response.status == 404:
            #got 404 , reset tag?
            print "404,reset tag?"
        return self.parse_htag(response)

    # Method for parsing a hastag
    def parse_htag(self, response):
        print "AGENT",response.request.headers['User-Agent'] 
        #Load it as a json object
        graphql = json.loads(response.text)
        has_next = graphql['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
        edges = graphql['graphql']['hashtag']['edge_hashtag_to_media']['edges']

        #if not hasattr(self, 'starting_shorcode') and len(edges):
        #    self.starting_shorcode = edges[0]['node']['shortcode']
        #    filename = self.checkpoint_path
        #    f = open(filename, 'w')
        #    f.write(self.starting_shorcode)

        for edge in edges:
            node = edge['node']
            if self.r.sismember('shortcodes',node['shortcode'])==0:
                self.count+=1
            else:
                self.punt+=1
            self.r.set(node['shortcode'], json.dumps(edge))
            self.r.sadd('shortcodes',node['shortcode'])
            self.r.sadd('shortcodes_'+self.hashtag,node['shortcode'])
            #print edge
            #print "XXX",edge
            #shortcode = node['shortcode']
            #if(self.checkAlreadyScraped(shortcode)):
            #    return
            #yield scrapy.Request("https://www.instagram.com/p/"+shortcode+"/?__a=1", callback=self.parse_post)
        now=int(time.time())
        sz=self.r.scard('shortcodes_'+self.hashtag)
        print "SPEED",self.count/float(now-self.start),"NEW",self.count,"PUNT",self.punt,"TOTAL",sz

        if has_next:
            end_cursor = graphql['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
            self.r.set("resume_"+self.hashtag, "https://www.instagram.com/explore/tags/"+self.hashtag+"/?__a=1&max_id="+end_cursor)
            #hits_per_hour=200.0
            #seconds_per_hit=(60.0*60.0)/hits_per_hour
            #time.sleep(seconds_per_hit)
            yield scrapy.Request("https://www.instagram.com/explore/tags/"+self.hashtag+"/?__a=1&max_id="+end_cursor, callback=self.parse_htag)
           
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
