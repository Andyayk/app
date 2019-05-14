import json
from flask import Flask, Response, json, jsonify, request, Blueprint, render_template
from py2neo import Graph, Node, Relationship #neo4j

app = Flask(__name__, static_folder='static', template_folder='static')
graph = Graph(password = "1234")

@app.route("/", methods=["GET"])
def get_index():
	return render_template("index.html")

@app.route("/graph", methods=["GET"])
def get_graph():
	query = '''
	MATCH (m:Movie)<-[:ACTED_IN]-(a:Person)
	RETURN m.title as movie, collect(a.name) as cast
	LIMIT {limit}
	'''

	results = graph.run(query, {"limit": 100})
	nodes = []
	rels = []

	i = 0
	for movie, cast in results:
		nodes.append({"title": movie, "label": "movie"})
		target = i
		i += 1

		for name in cast:
			actor = {"title": name, "label": "actor"}
			try:
				source = nodes.index(actor)
			except ValueError:
				nodes.append(actor)
				source = i
				i += 1
			rels.append({"source": source, "target": target})
			
	return jsonify({"nodes": nodes, "links": rels})

@app.route("/search", methods=["GET"])
def get_search():
	try:
		q = request.args.get('q')
	except KeyError:
		return []
	else:
		query = '''
		MATCH (movie:Movie)
		WHERE movie.title =~ {title}
		RETURN movie
		'''

		#get query that is case insensitive
		results = graph.run(query, {"title": "(?i).*" + q + ".*"})

		return jsonify([{"movie": dict(row["movie"])} for row in results])

@app.route("/movie/<title>", methods=["GET"])
def get_movie(title):
	query = '''
	MATCH (movie:Movie {title:{title}})
	OPTIONAL MATCH (movie)<-[r]-(person:Person)
	RETURN movie.title as title,
	collect([person.name, head(split(lower(type(r)),'_')), r.roles]) as cast
	LIMIT 1
	'''

	results = graph.run(query, {"title": title})
	row = results.next()

	return jsonify({"title": row["title"],
			"cast": [dict(zip(("name", "job", "role"), member)) for member in row["cast"]]})
