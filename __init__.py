import json, nltk
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import OneHotEncoder
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import *
from nltk.stem import WordNetLemmatizer
from nltk.probability import FreqDist
from flask import Flask, Response, json, jsonify, request, render_template, redirect, url_for
from py2neo import Graph, Node, Relationship #neo4j
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin

app = Flask(__name__, static_folder='static', template_folder='static') #static folder
app.config['SECRET_KEY'] = "a153246s35746d57f68g9uedtrfyughi98cyas" #secret key
graph = Graph(password = "1234") #neo4j database

login_manager = LoginManager() #flask login
login_manager.init_app(app) #initialise app

#user class
class User(UserMixin):
	def __init__(self, username, email, dateofbirth, jobtype, dateofhire):
		self.id = username
		self.email = email
		self.dateofbirth = dateofbirth
		self.jobtype = jobtype
		self.dateofhire = dateofhire

#default user loader
@login_manager.user_loader
def load_user(username):
	email = None
	dateofbirth = None
	jobtype = None
	dateofhire = None

	query = '''
	MATCH (node:User)
	WHERE node.username =~ {name}
	RETURN node.email as email, node.dateofbirth as dateofbirth, node.jobtype as jobtype, node.dateofhire as dateofhire 
	'''

	#get query
	results = graph.run(query, parameters={"name": username})

	for row in results:
		email = row['email']
		dateofbirth = row['dateofbirth']
		jobtype = row['jobtype']
		dateofhire = row['dateofhire']	

	return User(username, email, dateofbirth, jobtype, dateofhire)

#login page
@app.route('/')
@app.route('/login', methods = ['GET', 'POST'])
def login():
	message = None
   
	if request.method == 'POST':
		username = request.form.get('username') #get username
		password = request.form.get('password') #get password

		query = '''
		MATCH (node:User)
		WHERE node.username =~ {name}
		RETURN node.password as password
		'''

		querytest = '''
		MATCH (node:User)
		WHERE node.username =~ {name}
		RETURN node.password as password
		'''		

		#get query
		results = graph.run(query, parameters={"name": username})
		resultstest = graph.run(querytest, parameters={"name": username}) #checking if there are any results

		if resultstest.evaluate(): #if there are results
			for row in results:
				if row['password'] == password:
					user = load_user(username) #create user
					login_user(user) #login user
					return redirect(url_for('homepage'))
				else:
					message = "Incorrect Username/Password!" #message
		else:
			message = "Incorrect Username/Password!" #message

	if current_user.is_authenticated: #redirect user
		return render_template("index.html")
	else:
		return render_template('login.html', message = message)

#home page
@app.route("/homepage")
def homepage():
	if current_user.is_authenticated:
		return render_template("index.html")
	else:
		return render_template("login.html")

#register page
@app.route("/register", methods = ['GET', 'POST'])
def register():
	message = None
	if request.method == 'POST':
		username = request.form.get('username') #get username
		email = request.form.get('email') #get email
		dateofbirth = request.form.get('dateofbirth') #get date of birth
		jobtype = request.form.get('jobtype') #get job type
		dateofhire = request.form.get('dateofhire') #get date of hire
		password = request.form.get('password') #get password

		query = '''
		MATCH (node:User)
		WHERE node.username =~ {name}
		RETURN node
		'''

		querytest = '''
		MATCH (node:User)
		WHERE node.username =~ {name}
		RETURN node
		'''		

		#get query
		results = graph.run(query, parameters={"name": username})				
		resultstest = graph.run(querytest, parameters={"name": username}) #checking if there are any results

		if resultstest.evaluate(): #if there are results, user exists
			message = "Username already exists, please try again!"

			return render_template('register.html', message = message)
		else: #username doesn't exist
			user = Node("User", username=username, email=email, dateofbirth=dateofbirth, jobtype=jobtype, dateofhire=dateofhire, password=password) #creating respective user node
			graph.create(user)

			message = "Registered successfully. Please login!" #message
			return render_template('login.html', message = message)

	if current_user.is_authenticated: #redirect user
		return render_template("index.html")
	else:
		return render_template("register.html")

#logout the user
@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

#search for policies
@app.route("/search", methods=["POST"])
def search():
	try:
		stop_list = stopwords.words('english')
		stemmer = PorterStemmer()

		q = request.json['query']
		q2 = nltk.word_tokenize(q) #tokenize words
		q3 = [w.lower() for w in q2] #lowercase
		q4 = [w for w in q3 if re.search('^[a-z]+$', w)] #keep only alphabets
		q5 = [stemmer.stem(w) for w in q4] #stemming

	except KeyError:
		return []
	else:
		query = '''
		MATCH (node:Policy)
		WHERE node.name =~ {name}
		RETURN node
		'''

		querytest = '''
		MATCH (node:Policy)
		WHERE node.name =~ {name}
		RETURN node
		LIMIT 1
		'''		

		q6 = ""
		counter = 1
		for word in q5:
			q6 = q6 + word
			if counter < len(q5):
				q6 = q6 + "|"
			counter += 1
		
		#get query that is case insensitive
		results = graph.run(query, parameters={"name": "(?i).*(" + q6 + ").*"})
		resultstest = graph.run(querytest, parameters={"name": "(?i).*(" + q6 + ").*"}) #checking if there are any results

		if resultstest.evaluate(): #if there are results
			return jsonify(
				results = [{"policy": dict(row["node"])} for row in results]
			)
		else:
			return jsonify(
				results = [{"policy": {"name": "No Results Found!"}}]
			)	

#search for all related items of respective label
@app.route("/get_related/", methods=["GET"])
def get_related():
	name  = request.args.get('name')
	label  = request.args.get('label')

	if label == "Person": #so that it will only run once
		query = '''
		MATCH (node:User)
		WHERE node.username = {username}
		RETURN x
		'''
		user = graph.evaluate(query, parameters={"username": current_user.id}) #retrieve user node
		policy = Node("Policy", name=name) #creating a node

		relationship = Relationship.type('SEARCH') #changing it into a relationship type
		query2 = '''
		MATCH (node:User)-[s:SEARCH]->(p:Policy)
		WHERE p.name = {name}
		RETURN s.numsearch
		'''
		numsearch = graph.evaluate(query2, parameters={"name": name}) #retrieve numsearch
		
		if numsearch == None:
			numsearch = 1 #set numsearch as 1
		else:
			numsearch += 1 #increase numsearch

		graph.merge(relationship(user, policy, numsearch=numsearch), "Node", "name") #merging nodes with relationship		

	query = '''
	MATCH (node:%s)-[relatedTo]-(:Policy {name: {name}}) 
	RETURN node.name as name, Type(relatedTo) as relationship, node.text as text
	''' % (label) #string formatting

	querytest = '''
	MATCH (node:%s)-[relatedTo]-(:Policy {name: {name}}) 
	RETURN node.name as name, Type(relatedTo) as relationship, node.text as text
	LIMIT 1
	''' % (label) #string formatting

	results = graph.run(query, parameters={"name": name})
	resultstest = graph.run(querytest, parameters={"name": name}) #checking if there are any results

	dictionary = {}
	textlist = []

	if resultstest.evaluate(): #if there are results
		for row in results: #change into dictionary format
			relationship = row["relationship"]
			text = row['text']
			textlist.append(text)

			if relationship in dictionary:
				dictionary[relationship] = dictionary[relationship] + ", " + row["name"]
			else:
				dictionary[relationship] = row["name"]
		return jsonify(
			results = dictionary,
			textlist = textlist
		)
	else:
		return jsonify(
			results = None
		)

#User-Based Collaborative Filtering
@app.route("/recommend/", methods=["GET"])
def recommend():
	#policies data
	query = '''
	MATCH (node:Policy) 
	RETURN ID(node) as policyId, node.name as title
	'''
	policieslist = (list(graph.run(query))) #retrieve policies from database
	policies = pd.DataFrame(policieslist, columns=['policyId', 'title']) #create dataframe and rename columns

	#user data
	query2 = '''
	MATCH (node:User) 
	RETURN node.username as username, node.dateofbirth as dateofbirth, node.dateofhire as dateofhire, node.jobtype as jobtype, node.email as email, node.password as password
	'''
	userslist = (list(graph.run(query2))) #retrieve users from database
	users = pd.DataFrame(userslist, columns=['username', 'dateofbirth', 'dateofhire', 'jobtype', 'email', 'password']) #create dataeframe and rename columns	
	users = users.set_index('username') #set dataframe's index as username
	usersdf = pd.concat([users, pd.get_dummies(users['jobtype'], prefix='jobtype')], axis=1).drop(['jobtype'], axis=1) #one hot encoding
	usersdf['dateofbirth'] = pd.to_datetime(usersdf['dateofbirth'], format='%Y-%m-%d') #format date
	usersdf['dateofhire'] = pd.to_datetime(usersdf['dateofhire'], format='%Y-%m-%d') #format date

	usersdf['age'] = (pd.to_datetime('now') - usersdf['dateofbirth']).astype('<m8[D]') #calculate age
	usersdf['employmentage'] = (pd.to_datetime('now') - usersdf['dateofhire']).astype('<m8[D]') #calculate employment age

	usersdf = usersdf.drop(["dateofbirth", "dateofhire", "password", "email"], axis=1) #drop irrelevant columns

	#search data
	query3 = '''
	MATCH (node:User)-[s:SEARCH]->(p:Policy) 
	RETURN node.username as username, ID(p) as policyId, s.numsearch as numsearch
	'''
	searchlist = (list(graph.run(query3))) #retrieve searches from database
	searches = pd.DataFrame(searchlist, columns=['username', 'policyId', 'numsearch']) #create dataframe and rename columns
	print(searches.dtypes)
	mean = searches.groupby(by="username", as_index=False)['numsearch'].mean() #calculating mean search for each user
	search_avg = pd.merge(searches, mean, on='username') #add the mean column to dataframe
	search_avg['avg_search'] = search_avg['numsearch_x'] - search_avg['numsearch_y'] #calculate weighted average

	check = pd.pivot_table(search_avg, values='numsearch_x', index='username', columns='policyId') #for checking if user searched the policies already or not
	final = pd.pivot_table(search_avg, values='avg_search', index='username', columns='policyId') #creating pivot table for weighted average

	final_policy = final.fillna(final.mean(axis=0)) #replacing NaN by policies average
	final_policy = pd.merge(final_policy, usersdf, on='username') #add users columns to dataframe

	#user similarity on replacing NaN by item(policies) average
	cosine = cosine_similarity(final_policy) #normalized, penalise long documents
	np.fill_diagonal(cosine, 0) #fill diagonal with zeros
	similarity_with_policy = pd.DataFrame(cosine, index=final_policy.index) #create dataframe
	similarity_with_policy.columns = final_policy.index #change column names

	sim_user_m = find_n_neighbours(similarity_with_policy, 10) #top k neighbours for each user

	search_avg = search_avg.astype({"policyId": str})
	policy_user = search_avg.groupby(by = 'username')['policyId'].apply(lambda x:','.join(x))

	predicted_policies = user_policy_score(current_user.id, check, sim_user_m, policy_user, final_policy, mean, similarity_with_policy, policies)

	return jsonify(
		results = predicted_policies
	)

#k-nearest neighbours
def find_n_neighbours(df, n):
	order = np.argsort(df.values, axis=1)[:, :n]
	df = df.apply(lambda x: pd.Series(x.sort_values(ascending=False)
		.iloc[:n].index, 
		index=['top{}'.format(i) for i in range(1, n+1)]), 
		axis=1)
	return df

#sorting recommendations
def user_policy_score(user, check, sim_user_m, policy_user, final_policy, mean, similarity_with_policy, policies):
	policy_seen_by_user = check.columns[check[check.index==user].notna().any()].tolist()
	a = sim_user_m[sim_user_m.index==user].values
	b = a.squeeze().tolist()
	d = policy_user[policy_user.index.isin(b)]
	l = ','.join(d.values)
	policy_seen_by_similar_users = l.split(',')
	policies_under_consideration = list(set(policy_seen_by_similar_users)-set(list(map(str, policy_seen_by_user))))
	policies_under_consideration = list(map(int, policies_under_consideration))
	score = []
	for item in policies_under_consideration:
		c = final_policy.loc[:,item]
		d = c[c.index.isin(b)]
		f = d[d.notnull()]
		avg_user = mean.loc[mean['username'] == user,'numsearch'].values[0]
		index = f.index.values.squeeze().tolist()
		corr = similarity_with_policy.loc[user,index]
		fin = pd.concat([f, corr], axis=1)
		fin.columns = ['avg_score','correlation']
		fin['score']=fin.apply(lambda x:x['avg_score'] * x['correlation'],axis=1)
		nume = fin['score'].sum()
		deno = fin['correlation'].sum()
		final_score = avg_user + (nume/deno)
		score.append(final_score)
	data = pd.DataFrame({'policyId':policies_under_consideration,'score':score})
	top_5_recommendation = data.sort_values(by='score',ascending=False).head(5)
	policy_name = top_5_recommendation.merge(policies, how='inner', on='policyId')
	policy_names = policy_name.title.values.tolist()
	return policy_names

"""
Neo4j Commands:

LOAD CSV WITH HEADERS FROM 'file:///searches.csv' AS line
MATCH (node:User {username: line.username})
MATCH (p:Policy) WHERE ID(p) = toInt(line.policyId)
MERGE (node)-[s:SEARCH {numsearch: line.numsearch}]->(p)

CREATE (ee:Person {name: 'Emil'})

MATCH (ee:Person) WHERE ee.name = "Emil" RETURN ee

MATCH (ee:PERSON)-[:KNOWS]-(friends) WHERE ee.name = "Emil" RETURN ee, friends

WITH -> Manipulate the output before it is passed on
COLLECT -> Group by
REDUCE -> Iterate in each element and run the expression
MATCH (n) DETACH DELETE n
"""