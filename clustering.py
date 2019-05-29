import nltk, re, k_means, gensim, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
from sklearn.cluster import KMeans, AgglomerativeClustering
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import *
from nltk.stem import WordNetLemmatizer
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn import metrics
from pandas import DataFrame
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import dendrogram, linkage

directory = os.getcwd() + '/documents2' #documents directory

df = pd.DataFrame() #empty dataframe

for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        df2 = pd.read_csv(directory + '/' + filename, sep="!", header=None, encoding='latin-1') #read text file into dataframe
        df = df.append(df2, ignore_index = True) #append dataframe

columnName = 'text'
df.columns = [columnName] #set column names
print(df)
listOfTokenizedWords = []
for x in df[columnName]:
    tokenized_word = word_tokenize(x) #tokenize each row and save into dataframe
    listOfTokenizedWords.append(tokenized_word)

df[columnName] = listOfTokenizedWords #replace original words with tokenize words

#change all to lowercase letters
df[columnName] = df[columnName].apply(lambda x: [y.lower() for y in x])

#keep only alphabets
df[columnName] = df[columnName].apply(lambda x: [y for y in x if re.search('^[a-z]+$', y)])

#remove stopwords
stop_list = stopwords.words('english')
stop_list += ['would', 'said', 'say', 'year', 'day', 'also', 'first', 'last', 'one', 'two', 'people', 'told', 'new', \
'could', 'three', 'may', 'like', 'world', 'since', 'rt', 'http', 'https'] 
           
df[columnName] = df[columnName].apply(lambda x: [y for y in x if y not in stop_list])

#stemming each tweet
stemmer = PorterStemmer()
df[columnName] = df[columnName].apply(lambda x: [stemmer.stem(y) for y in x])

#remove single and double letters
df[columnName] = df[columnName].apply(lambda x: [y for y in x if len(y) >= 3])

#convert processed tweets from dataframe to a list
processedWords = df[columnName].tolist()

#rejoin the tokenize words into a sentence after preprocessing as count vectorizer need it to be a string
stringOfTokenizedWords = []
for x in processedWords:
    sentence = (' '.join(x))
    stringOfTokenizedWords.append(sentence)

vectorizer = TfidfVectorizer(analyzer='word') #tfidf
words_tfidf = vectorizer.fit_transform(stringOfTokenizedWords) #tfidf

features = vectorizer.get_feature_names() #get list of features

processeddf = pd.DataFrame(words_tfidf.toarray(), columns=features) #creating dataframe

sse = {}
for k in range(1, 30):
    kmeans = KMeans(n_clusters=k, max_iter=1000).fit(processeddf)
    processeddf["clusters"] = kmeans.labels_
    #print(processeddf["clusters"])
    sse[k] = kmeans.inertia_ #inertia: Sum of distances of samples to their closest cluster center

plt.figure()
plt.plot(list(sse.keys()), list(sse.values()))
plt.xlabel("Number of cluster")
plt.ylabel("SSE")
plt.show()

#cluster = AgglomerativeClustering(n_clusters=2, affinity='euclidean', linkage='ward')  
#cluster.fit(processeddf) 

Z = linkage(processeddf)
plt.figure()
dendrogram(Z)
plt.show()