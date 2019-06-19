import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances

#User-Based Collaborative Filtering

policies = pd.read_csv("policies.csv", encoding="Latin1") #read csv to dataframe
searches = pd.read_csv("searches.csv") #read csv to dataframe

mean = searches.groupby(by="userId", as_index=False)['numsearch'].mean() #calculating the mean search for each user
search_avg = pd.merge(searches, mean, on='userId')
search_avg['adg_search'] = search_avg['numsearch_x'] - search_avg['numsearch_y']

check = pd.pivot_table(search_avg, values='numsearch_x', index='userId', columns='policyId')
final = pd.pivot_table(search_avg, values='adg_search', index='userId', columns='policyId')

#replacing NaN by Movie Average
final_movie = final.fillna(final.mean(axis=0))

#replacing NaN by user Average
final_user = final.apply(lambda row: row.fillna(row.mean()), axis=1)

#user similarity on replacing NaN by user avg
b = cosine_similarity(final_user)
np.fill_diagonal(b, 0) #fill diagonal with zeros
similarity_with_user = pd.DataFrame(b, index=final_user.index)
similarity_with_user.columns = final_user.index

#user similarity on replacing NaN by item(policies) avg
cosine = cosine_similarity(final_movie)
np.fill_diagonal(cosine, 0) #fill diagonal with zeros
similarity_with_movie = pd.DataFrame(cosine, index=final_movie.index)
similarity_with_movie.columns = final_user.index

"""
def get_user_similar_movies(user1, user2):
	common_movies = search_avg[search_avg.userId == user1].merge(
	search_avg[search_avg.userId == user2],
	on = "policyId",
	how = "inner" )
	return common_movies.merge( policies, on = 'policyId' )

a = get_user_similar_movies(370, 86309)
a = a.loc[ : , ['rating_x_x', 'rating_x_y', 'title']]
"""

def find_n_neighbours(df, n):
	order = np.argsort(df.values, axis=1)[:, :n]
	df = df.apply(lambda x: pd.Series(x.sort_values(ascending=False)
		   .iloc[:n].index, 
		  index=['top{}'.format(i) for i in range(1, n+1)]), axis=1)
	return df

#top 30 neighbours for each user
sim_user_30_u = find_n_neighbours(similarity_with_user, 2)

#top 30 neighbours for each user
sim_user_30_m = find_n_neighbours(similarity_with_movie, 2)

"""
def User_item_score(user, item):
	a = sim_user_30_m[sim_user_30_m.index==user].values
	b = a.squeeze().tolist()
	c = final_movie.loc[:,item]
	d = c[c.index.isin(b)]
	f = d[d.notnull()]
	avg_user = mean.loc[mean['userId'] == user,'numsearch'].values[0]
	index = f.index.values.squeeze().tolist()
	corr = similarity_with_movie.loc[user,index]
	fin = pd.concat([f, corr], axis=1)
	fin.columns = ['adg_score','correlation']
	fin['score']=fin.apply(lambda x:x['adg_score'] * x['correlation'],axis=1)
	nume = fin['score'].sum()
	deno = fin['correlation'].sum()
	final_score = avg_user + (nume/deno)
	return final_score

score = User_item_score(320, 7371)
print("score (u,i) is", score)
"""

search_avg = search_avg.astype({"policyId": str})
Movie_user = search_avg.groupby(by = 'userId')['policyId'].apply(lambda x:','.join(x))

def User_item_score1(user):
	Movie_seen_by_user = check.columns[check[check.index==user].notna().any()].tolist()
	a = sim_user_30_m[sim_user_30_m.index==user].values
	b = a.squeeze().tolist()
	d = Movie_user[Movie_user.index.isin(b)]
	l = ','.join(d.values)
	Movie_seen_by_similar_users = l.split(',')
	Movies_under_consideration = list(set(Movie_seen_by_similar_users)-set(list(map(str, Movie_seen_by_user))))
	Movies_under_consideration = list(map(int, Movies_under_consideration))
	score = []
	for item in Movies_under_consideration:
		c = final_movie.loc[:,item]
		d = c[c.index.isin(b)]
		f = d[d.notnull()]
		avg_user = mean.loc[mean['userId'] == user,'numsearch'].values[0]
		index = f.index.values.squeeze().tolist()
		corr = similarity_with_movie.loc[user,index]
		fin = pd.concat([f, corr], axis=1)
		fin.columns = ['adg_score','correlation']
		fin['score']=fin.apply(lambda x:x['adg_score'] * x['correlation'],axis=1)
		nume = fin['score'].sum()
		deno = fin['correlation'].sum()
		final_score = avg_user + (nume/deno)
		score.append(final_score)
	data = pd.DataFrame({'policyId':Movies_under_consideration,'score':score})
	top_5_recommendation = data.sort_values(by='score',ascending=False).head(5)
	Movie_Name = top_5_recommendation.merge(policies, how='inner', on='policyId')
	Movie_Names = Movie_Name.title.values.tolist()
	return Movie_Names

user = int(input("Enter the user id to whom you want to recommend : "))
predicted_movies = User_item_score1(user)
print(" ")
print("The Recommendations for User Id : ", user)
print("   ")
for i in predicted_movies:
	print(i)