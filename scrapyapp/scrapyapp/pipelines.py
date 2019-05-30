# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
from py2neo import Graph, Node, Relationship #neo4j
from scrapyapp.items import HRPolicyRelationItem, DocumentItem

path = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "documents") #setting directory to save in
graph = Graph(password = "1234") #neo4j database

class ScrapyappPipeline(object):

	def __init__(self):
		pass

	def process_item(self, item, spider):
		self.store_db(item)
		return item

	def store_db(self, item):
		if isinstance(item, HRPolicyRelationItem):
			policy = Node("Policy", name=item['policyname']) #creating a node
			relationshiptext = item['relationship'].upper() #relationship text
			personname = item['name'].strip()

			if "(view" in personname:
				personname = personname[:-6] #get everything except the last 5 letters

			personnamelist = personname.split(",") #splitting names by commas

			for personname in personnamelist:
				personname = personname.strip() #trimming whitespaces

				person = Node("Person", name=personname) #creating a node
				relationship = Relationship.type(relationshiptext) #changing it into a relationship type
				graph.merge(relationship(person, policy), "Node", "name") #merging nodes with relationship

		elif isinstance(item, DocumentItem):
			file = open(path + os.sep + item['policyname'] + ".txt","w") #saving data into text file
			file.write(item['document'])
			file.close()