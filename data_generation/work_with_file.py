import pandas as pd
import numpy as np

dfy = pd.read_excel('Amazon_top100_bestselling_books_2009to2021.xlsx', dtype={"no_of_reviews": str})
dfy.drop(columns=['Unnamed: 0'], inplace=True)

...
"Replacing null values in the continous varible"
...

dfy['no_of_reviews'] = dfy['no_of_reviews'].fillna(dfy['no_of_reviews'].median())
dfy['price'] = dfy['price'].fillna(dfy['price'].mean())
dfy['ratings'] = dfy['ratings'].fillna(dfy['ratings'].mode())
dfy.dropna(inplace=True)
dfy.no_of_reviews = dfy.no_of_reviews.astype(int)
dfy.price = dfy.price.astype(float)
dfy.ranks = dfy.ranks.astype(int)
dfy.drop(dfy.loc[dfy['genre']== 'unknown'].index, inplace=True)

dfy.head()
