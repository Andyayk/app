import gensim
from gensim import similarities

import random

num_iterations = 200

def k_means(vecs, V, K):
    # get the number of vectors
    N = len(vecs)

    # build an index from the input vectors
    index = similarities.SparseMatrixSimilarity(vecs, V)
    
    # store the cluster centers in the following array
    centers = []
    
    # store the indices of the vectors belonging to different clusters in the following array
    clusters = []
    
    # initialize the cluster centers
    
    # the center of the first cluster is randomly chosen
    cid = random.randint(0, N - 1)
    centers.append(vecs[cid])
    
    # the center of the following clusters are chosen in such a way that they are far away from each other
    for k in range(1, K):
        sims = []
        for n in range(N):
            sims.append((n, 0.0))
        for l in range(k):
            cur_sims = list(enumerate(index[centers[l]]))
            for n in range(N):
                sims[n] = (n, sims[n][1] + cur_sims[n][1])
        sorted_sims = sorted(sims, key=lambda item: item[1])
        cid = sorted_sims[0][0]
        centers.append(vecs[cid])
    
    # iteratively re-assign vectors to clusters
    for j in range(num_iterations):
        
        # compute the similarities between the cluster centers to each vector
        sims = [list(enumerate(index[c])) for c in centers]
        
        clusters = []
        for k in range(K):
            clusters.append([])
        
        # for each vector, assign it to a cluster based on which cluster center is the closest to it
        for n in range(N):
            scores = [(k, sims[k][n]) for k in range(K)]
            sorted_scores = sorted(scores, key=lambda item: -item[1][1])
            c = sorted_scores[0][0]
            clusters[c].append(n)
        
        # update the cluster centers
        centers = []
        for k in range(K):
            centers.append(compute_center(vecs, clusters[k]))
            
    return clusters
    
def compute_center(vecs, cluster):
    sum = {}
    for n in cluster:
        vec = vecs[n]
        for (id, val) in vec:
            if (id in sum):
                sum[id] = sum[id] + val
            else:
                sum[id] = val
    
    size = len(cluster)
    
    sorted_keys = sorted(sum.keys(), key=lambda item: item)
    
    center = []
    for key in sorted_keys:
        center.append((key, sum[key]/size))
    
    return center