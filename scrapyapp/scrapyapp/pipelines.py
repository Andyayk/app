# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import mysql.connector, os
from py2neo import Graph, Node, Relationship #neo4j
from scrapyapp.items import HRPolicyRelationItem, DocumentItem

path = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "documents")
graph = Graph(password = "1234")

class ScrapyappPipeline(object):

    def __init__(self):
        pass

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self, item):
        if isinstance(item, HRPolicyRelationItem):
            policy = Node("Policy", name=item['policyname'])
            relationship = item['relationship'].upper()

            if relationship == 'REVIEWED BY':
                personlist = item['name'].split(",")

                for p in personlist:
                    person = Node("Person", name=p)
                    relationship = Relationship.type(relationship)
                    graph.merge(relationship(person, policy), "Person", "name")
            else:
                person = Node("Person", name=item['name'])
                relationship = Relationship.type(relationship)
                graph.merge(relationship(person, policy), "Person", "name")

        elif isinstance(item, DocumentItem):
            file = open(path + os.sep + item['policyname'] + ".txt","w") 
            file.write(item['document'])
            file.close()

    '''
    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        self.conn = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            passwd = '',
            database = 'scrapyapp'
        )
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute("""DROP TABLE IF EXISTS scrapyapp""")
        self.curr.execute("""create table scrapyapp(
                        title text,
                        author text,
                        tag text
                        )""")

    def store_db(self, item):
        results = graph.run(query, {"limit": 500})

        self.curr.execute("""insert into scrapyapp values (%s, %s, %s)""", (
            item['title'][0],
            item['author'][0],
            item['tag'][0]
        ))
        self.conn.commit()                      
    '''