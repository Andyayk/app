import nltk, re, k_means, gensim, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import *
from nltk.stem import WordNetLemmatizer
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn import metrics
from pandas import DataFrame
from sklearn.metrics.pairwise import cosine_similarity


directory = os.getcwd() + '/documents' #documents directory

df = pd.DataFrame() #empty dataframe

for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        df2 = pd.read_csv(directory + '/' + filename, sep="!", header=None, encoding='latin-1') #read text file into dataframe
        df = df.append(df2, ignore_index = True) #append dataframe

columnName = 'text'
df.columns = [columnName] #set column names

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

#terms = vectorizer.get_feature_names()

#df3 = pd.DataFrame(words_tfidf.toarray(), columns=terms) #creating dataframe

#dist = 1 - cosine_similarity(words_tfidf)

num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters).fit(words_tfidf)
clusters = kmeans.labels_.tolist()

print(clusters)
print(kmeans.cluster_centers_)

'''
stop_list = nltk.corpus.stopwords.words('english')
stemmer = nltk.stem.porter.PorterStemmer()

def load_corpus(dir):
    #dir is a directory with plain text files to load
    corpus = nltk.corpus.PlaintextCorpusReader(dir, '.+\.txt', encoding='latin-1')
    return corpus

def corpus2docs(corpus):
    #corpus is a object returned by load_corpus that represents a corpus
    fids = corpus.fileids()
    docs1 = []
    for fid in fids:
        doc_raw = corpus.raw(fid)
        doc = nltk.word_tokenize(doc_raw) #tokenize words
        docs1.append(doc)

    docs2 = [[w.lower() for w in doc] for doc in docs1] #lowercase
    docs3 = [[w for w in doc if re.search('^[a-z]+$', w)] for doc in docs2] #keep only alphabets
    docs4 = [[w for w in doc if w not in stop_list] for doc in docs3] #remove stopwords
    docs5 = [[stemmer.stem(w) for w in doc] for doc in docs4] #stemming
    docs6 = [[w for w in doc if len(w) >= 3] for doc in docs5] #remove single and double letters

    return docs6

def docs2vecs(docs, dictionary):
    #docs is a list of documents returned by corpus2docs
    #dictionary is a gensim.corpora.Dictionary object
    vecs1 = [dictionary.doc2bow(doc) for doc in docs]
    tfidf = gensim.models.TfidfModel(vecs1) #TF-IDF
    vecs2 = [tfidf[vec] for vec in vecs1]
    return vecs2

corpus = load_corpus('documents')
docs = corpus2docs(corpus)
dictionary = gensim.corpora.Dictionary(docs)
vecs = docs2vecs(docs, dictionary)

print(len(docs))

num_tokens = len(dictionary.token2id)
clusters = k_means.k_means(vecs, num_tokens, 13)

#the below prints the file ids in each cluster
fids = corpus.fileids()
counter = 1

for cluster in clusters:
   print(counter, [fids[d] for d in cluster])
   counter += 1

#take all the file IDs in cluster1
cluster1 = clusters[0]
cluster1_fids = [fids[d] for d in cluster1]

#create an empty list clust1_words =[]
cluster1_all_words = []

#add the words from all files to this list. Use corpus.words and extend method
for fid in cluster1_fids:
    cluster1_all_words.extend(corpus.words(fid))
    
#remove the Stopwords from this list
stop_list = nltk.corpus.stopwords.words('english')

all_words1 = [w.lower() for w in cluster1_all_words]
all_words2 = [w for w in all_words1 if w not in stop_list and len(w)>3]

#call freq distribution metod and display top 10 words or 20 words
fdist = nltk.FreqDist(all_words2)
print(fdist.most_common(10))
'''