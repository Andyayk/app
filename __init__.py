import json, nltk
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
	def __init__(self, username, email, dateofbirth, jobtype, datejoined):
		self.id = username
		self.email = email
		self.dateofbirth = dateofbirth
		self.jobtype = jobtype
		self.datejoined = datejoined

#default user loader
@login_manager.user_loader
def load_user(username):
	email = None
	dateofbirth = None
	jobtype = None
	datejoined = None

	query = '''
			MATCH (node:User)
			WHERE node.username =~ {name}
			RETURN node.email as email, node.dateofbirth as dateofbirth, node.jobtype as jobtype, node.datejoined as datejoined 
			'''

	#get query
	results = graph.run(query, parameters={"name": username})

	for row in results:
		email = row['email']
		dateofbirth = row['dateofbirth']
		jobtype = row['jobtype']
		datejoined = row['datejoined']	

	return User(username, email, dateofbirth, jobtype, datejoined)

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
		datejoined = request.form.get('datejoined') #get date joined
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
			user = Node("User", username=username, email=email, dateofbirth=dateofbirth, jobtype=jobtype, datejoined=datejoined, password=password) #creating respective user node
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