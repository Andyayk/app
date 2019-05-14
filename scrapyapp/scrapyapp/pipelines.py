# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import mysql.connector
from py2neo import Graph, Node, Relationship #neo4j
from scrapyapp.items import HRPolicyRelationItem, DocumentItem, HRPolicyInfoItem

graph = Graph(password = "1234")

class ScrapyappPipeline(object):

    def __init__(self):
        pass

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self, item):
        if isinstance(item, HRPolicyInfoItem):
            query = '''
            CREATE (:Policy {name:{policyname}})
            '''
            results = graph.run(query, {"policyname": item['policyname']})

        elif isinstance(item, HRPolicyRelationItem):
            a = Node("Person", name=item['name'])
            b = Node("Policy", name=item['policyname'])
            relationship = Relationship.type(item['relationship'].upper())
            graph.merge(relationship(a, b), "Person", "name")

        elif isinstance(item, DocumentItem):
            pass

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