import pandas as pd 
import numpy as np
import warnings
warnings.filterwarnings('ignore')

#read csv
df = pd.read_csv('train.csv', sep=',')
print(df.head())

print(df.describe())

#sort
numsearch = pd.DataFrame(df.groupby('policy')['numsearch'].mean())
print(numsearch.head())

#convert to dataframe matrix, policy as columns
policy_matrix = df.pivot_table(index='username', columns='policy', values='numsearch')
print(policy_matrix.head())

#retrieve columns
APP_user_search = policy_matrix['Academic pay policy']
promotion_user_search = policy_matrix['Academic promotion']
print(APP_user_search.head())
print(promotion_user_search.head())

#find similarities
similar_to_APP = policy_matrix.corrwith(APP_user_search)
print(similar_to_APP.head())

#find similarities
similar_to_promotion = policy_matrix.corrwith(promotion_user_search)
print(similar_to_promotion.head())

#convert to dataframe
corr_APP = pd.DataFrame(similar_to_APP, columns=['correlation'])
corr_APP.dropna(inplace=True)
print(corr_APP.head())

#convert to dataframe
corr_promotion = pd.DataFrame(similar_to_promotion, columns=['Correlation'])
corr_promotion.dropna(inplace=True)
print(corr_promotion.head())