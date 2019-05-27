import nltk, re, k_means, gensim

stop_list = nltk.corpus.stopwords.words('english')
stemmer = nltk.stem.porter.PorterStemmer()

def load_corpus(dir):
    # dir is a directory with plain text files to load.
    corpus = nltk.corpus.PlaintextCorpusReader(dir, '.+\.txt', encoding='latin-1')
    return corpus

def corpus2docs(corpus):
    # corpus is a object returned by load_corpus that represents a corpus.
    fids = corpus.fileids()
    docs1 = []
    for fid in fids:
        doc_raw = corpus.raw(fid)
        doc = nltk.word_tokenize(doc_raw)
        docs1.append(doc)
    docs2 = [[w.lower() for w in doc] for doc in docs1]
    docs3 = [[w for w in doc if re.search('^[a-z]+$', w)] for doc in docs2]
    docs4 = [[w for w in doc if w not in stop_list] for doc in docs3]
    docs5 = [[stemmer.stem(w) for w in doc] for doc in docs4]
    return docs5

def docs2vecs(docs, dictionary):
    # docs is a list of documents returned by corpus2docs.
    # dictionary is a gensim.corpora.Dictionary object.
    vecs1 = [dictionary.doc2bow(doc) for doc in docs]
    tfidf = gensim.models.TfidfModel(vecs1)
    vecs2 = [tfidf[vec] for vec in vecs1]
    return vecs2

corpus = load_corpus('documents')

docs = corpus2docs(corpus)

dictionary = gensim.corpora.Dictionary(docs)

vecs = docs2vecs(docs, dictionary)
print(len(docs))

num_tokens = len(dictionary.token2id)
clusters = k_means.k_means(vecs, num_tokens, 10)

fids = corpus.fileids()

#The below prints the file ids in each cluster

counter = 1

for cluster in clusters:
   print(counter, [fids[d] for d in cluster])
   counter += 1