import pickle
import pandas as pd
from py2neo import Graph, Node, Relationship #neo4j

graph = Graph(password = "1234") #neo4j database

def createRelationship(relatedtermname, policy, text):
	relationshiptext = 'RELATED'
	relatedterm = Node("RelatedTerm", name=relatedtermname, text=text) #creating a node
	relationship = Relationship.type(relationshiptext) #changing it into a relationship type
	graph.merge(relationship(relatedterm, policy), "Node", "name") #merging nodes with relationship

processeddf = pd.read_pickle("processeddf") #read pickle

clusters = processeddf['clusters'].tolist()
filenames = processeddf['filename'].tolist()
textlist = processeddf['text'].tolist()
policies = {
	1 : 'Retirement policy',
	0 : 'Leave policy (with effect from 01.01.2017)'
	}

for num, cluster in enumerate(clusters):
	relatedtermname = filenames[num] #retrieve document name
	text = textlist[num] #retrieve body text
	policy = Node("Policy", name=policies[cluster]) #creating respective policy node
	createRelationship(relatedtermname, policy, text)