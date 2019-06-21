import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import OneHotEncoder

#User-Based Collaborative Filtering

policies = pd.read_csv("policies.csv", encoding="Latin1") #read csv to dataframe
searches = pd.read_csv("searches.csv") #read csv to dataframe
users = pd.read_csv("users.csv") #read csv to dataframe
users = users.set_index('username')
usersdf = pd.concat([users, pd.get_dummies(users['jobtype'], prefix='jobtype')], axis=1).drop(['jobtype'], axis=1)

usersdf['dateofbirth'] = pd.to_datetime(usersdf['dateofbirth'], format='%Y-%m-%d')
usersdf['dateofhire'] = pd.to_datetime(usersdf['dateofhire'], format='%Y-%m-%d')

usersdf['age'] = (pd.to_datetime('now') - usersdf['dateofbirth']).astype('<m8[D]')
usersdf['employmentage'] = (pd.to_datetime('now') - usersdf['dateofhire']).astype('<m8[D]')

usersdf = usersdf.drop(["dateofbirth", "dateofhire"], axis=1) #drop dates
print(usersdf)

mean = searches.groupby(by="username", as_index=False)['numsearch'].mean() #calculating mean search for each user
search_avg = pd.merge(searches, mean, on='username') #add the mean column to dataframe
search_avg['avg_search'] = search_avg['numsearch_x'] - search_avg['numsearch_y'] #calculate weighted average

check = pd.pivot_table(search_avg, values='numsearch_x', index='username', columns='policyId') #for checking if user searched the policies already or not
final = pd.pivot_table(search_avg, values='avg_search', index='username', columns='policyId') #creating pivot table for weighted average

final_policy = final.fillna(final.mean(axis=0)) #replacing NaN by policies average
final_policy = pd.merge(final_policy, usersdf, on='username') #add users columns to dataframe
print(final_policy)

"""
final_user = final.apply(lambda row: row.fillna(row.mean()), axis=1) #replacing NaN by user average

#user similarity on replacing NaN by user average
b = cosine_similarity(final_user)
np.fill_diagonal(b, 0) #fill diagonal with zeros
similarity_with_user = pd.DataFrame(b, index=final_user.index)
similarity_with_user.columns = final_user.index
"""

#user similarity on replacing NaN by item(policies) average
cosine = cosine_similarity(final_policy) #normalized
np.fill_diagonal(cosine, 0) #fill diagonal with zeros
similarity_with_policy = pd.DataFrame(cosine, index=final_policy.index) #create dataframe
similarity_with_policy.columns = final_policy.index #change column names
print(similarity_with_policy)

"""
def get_user_similar_policies(user1, user2):
	common_policies = search_avg[search_avg.username == user1].merge(
	search_avg[search_avg.username == user2],
	on = "policyId",
	how = "inner" )
	return common_policies.merge( policies, on = 'policyId' )

a = get_user_similar_policies(370, 86309)
a = a.loc[ : , ['rating_x_x', 'rating_x_y', 'title']]
"""

def find_n_neighbours(df, n):
	order = np.argsort(df.values, axis=1)[:, :n]
	df = df.apply(lambda x: pd.Series(x.sort_values(ascending=False)
		.iloc[:n].index, 
		index=['top{}'.format(i) for i in range(1, n+1)]), 
		axis=1)
	return df

"""
sim_user_u = find_n_neighbours(similarity_with_user, 10) #top k neighbours for each user
"""

sim_user_m = find_n_neighbours(similarity_with_policy, 10) #top k neighbours for each user
print(sim_user_m)

"""
def user_item_score(user, item):
	a = sim_user_m[sim_user_m.index==user].values
	b = a.squeeze().tolist()
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
	return final_score

score = user_item_score(320, 7371)
print("score (u,i) is", score)
"""

search_avg = search_avg.astype({"policyId": str})
policy_user = search_avg.groupby(by = 'username')['policyId'].apply(lambda x:','.join(x))

def user_policy_score(user):
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

user = input("Enter the username to whom you want to recommend : ")
predicted_policies = user_policy_score(user)
print(" ")
print("The recommendations for username are : ", user)
print("   ")

for i in predicted_policies:
	print(i)