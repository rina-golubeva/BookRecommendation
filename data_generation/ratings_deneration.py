import pandas as pd
import numpy as np

''Repeating the actions of the data_generation file'''

dfy = pd.read_excel('Amazon_top100_bestselling_books_2009to2021.xlsx', dtype={"no_of_reviews": str})
dfy.drop(columns=['Unnamed: 0'], inplace=True)
dfy['no_of_reviews'] = dfy['no_of_reviews'].str.replace(',', '').astype(float)
dfy['no_of_reviews']= pd.to_numeric(dfy['no_of_reviews'])
dfy['no_of_reviews'] = dfy['no_of_reviews'].fillna(dfy['no_of_reviews'].median())
dfy['price'] = dfy['price'].fillna(dfy['price'].mean())
dfy['ratings'] = dfy['ratings'].fillna(dfy['ratings'].mode())
dfy.dropna(inplace=True)
dfy.no_of_reviews = dfy.no_of_reviews.astype(int)
dfy.price = dfy.price.astype(float)
dfy.ranks = dfy.ranks.astype(int)
dfy.drop(dfy.loc[dfy['genre']== 'unknown'].index, inplace=True)

'''Creating a dictionary to address critics and a dictionary to address a book'''

names=dfy['title']
names.drop_duplicates()
names=names.to_list()
names=list(map(str,names))
names=sorted(list(set(names)))
d={}
from random import randint
for i in names:
  d[i]=[randint(0,5) for j in range(101)]
d=pd.DataFrame(d)
d_trans=d.T
books=d.to_dict()
critics=d_trans.to_dict()
