# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags

class HRPolicyRelationItem(scrapy.Item):
	relationship = scrapy.Field()
	name = scrapy.Field()
	policyname = scrapy.Field()

class DocumentItem(scrapy.Item):
	document = scrapy.Field()
	policyname = scrapy.Field()