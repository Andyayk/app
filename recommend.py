import pandas as pd 
import numpy as np
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('u.data', sep='\t', names=['user_id','item_id','rating','titmestamp'])

print(df.head())

movie_titles = pd.read_csv('Movie_Id_Titles')
print(movie_titles.head())

df = pd.merge(df, movie_titles, on='item_id')
print(df.head())

print(df.describe())

ratings = pd.DataFrame(df.groupby('title')['rating'].mean())
print(ratings.head())

ratings['number_of_ratings'] = df.groupby('title')['rating'].count()
print(ratings.head())

movie_matrix = df.pivot_table(index='user_id', columns='title', values='rating')
print(movie_matrix.head())

print(ratings.sort_values('number_of_ratings', ascending=False).head(10))

AFO_user_rating = movie_matrix['Air Force One (1997)']
contact_user_rating = movie_matrix['Contact (1997)']

print(AFO_user_rating.head())
print(contact_user_rating.head())

similar_to_air_force_one = movie_matrix.corrwith(AFO_user_rating)
print(similar_to_air_force_one.head())

similar_to_contact = movie_matrix.corrwith(contact_user_rating)
print(similar_to_contact.head())

corr_AFO = pd.DataFrame(similar_to_air_force_one, columns=['correlation'])
corr_AFO.dropna(inplace=True)
print(corr_AFO.head())

corr_contact = pd.DataFrame(similar_to_contact, columns=['Correlation'])
corr_contact.dropna(inplace=True)
print(corr_contact.head())

corr_AFO = corr_AFO.join(ratings['number_of_ratings'])
corr_contact = corr_contact.join(ratings['number_of_ratings'])

print(corr_AFO[corr_AFO['number_of_ratings'] > 100].sort_values(by='correlation', ascending=False).head(10))

print(corr_contact[corr_contact['number_of_ratings'] > 100].sort_values(by='Correlation', ascending=False).head(10))

