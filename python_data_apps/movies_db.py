from flask import *
import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures, OneHotEncoder
from sklearn.linear_model import LinearRegression, Lasso, LassoCV, Ridge, RidgeCV
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
import seaborn as sns

import matplotlib
import matplotlib.pyplot as plt


def get_movie_data():
    #Read in csvs and set index
    mojo = pd.read_csv('data/mojo_revised.csv')
    imdb = pd.read_csv('data/imdb.csv')
    metacritic = pd.read_csv('data/metacritic.csv')
    tomato = pd.read_csv('data/rotten_tomatoes.csv')
    heirloom = pd.read_csv('data/heirloom.csv')
    mojo.rename(columns={"title": "mojo_title"}, inplace=True)
    heirloom.set_index(['mojo_title'])
    mojo.set_index(['mojo_title'])
    imdb.set_index(['mojo_title'])
    metacritic.set_index(['mojo_title'])
    tomato.set_index(['mojo_title'])

    tomato_final = tomato.merge(heirloom, on='mojo_title', how='left')
    tomato_final = tomato_final.drop(['url_y', 'tomato_criticcount_x'], axis=1)
    tomato_final = tomato_final.rename(columns={"tomato_criticcount_y":"tomato_criticcount", "url_x":"url"})
    tomato_final = tomato_final.dropna(subset=['tomato_image'])

    def get_img_url(df):
        return re.findall('(?<=data-src).*$', df)[0][2:-2]
    tomato_final['tomato_image'] = tomato_final['tomato_image'].apply(get_img_url)

    mojo['release_year'] = [x.strip()[-4:] for x in mojo['release_days'].astype(str)]

    mojo.drop_duplicates(subset='mojo_title', inplace=True)
    imdb.drop_duplicates(subset='mojo_title', inplace=True)
    df1 = mojo.merge(imdb, on='mojo_title', how='left')
    metacritic.drop_duplicates(subset='mojo_title', inplace=True)
    df2 = df1.merge(metacritic, on='mojo_title', how='left')
    tomato_final.drop_duplicates(subset='mojo_title', inplace=True)

    df = df2.merge(tomato_final, on='mojo_title', how='left')

    df['tomato_audiencescore'] =pd.to_numeric(df['tomato_audiencescore'])
    df['tomato_criticscore'] =pd.to_numeric(df['tomato_criticscore'])
    df['tomato_criticscore'].fillna(df['tomato_criticscore'].mean())
    df['tomato_audiencescore'].fillna(df['tomato_audiencescore'].mean())
    df['tomato_title'].fillna(df['mojo_title'])
    df[df['imdbscore'] == 'Link error'] = np.nan

    df['mc_criticscore'].isnull().sum(axis=0)

    df['mc_criticscore'] = df['mc_criticscore'].replace(['Link error'],np.nan)
    df['mc_criticscore'] = df['mc_criticscore'].replace(['tbd'],np.nan)
    df['mc_criticscore'] = df['mc_criticscore'].replace(['No score yet'],np.nan)
    df['mc_criticcount'] = df['mc_criticcount'].replace(['Link error'],np.nan)
    df['mc_criticcount'] = df['mc_criticcount'].replace(['tbd'],np.nan)

    df['mc_audiencecount'] = df['mc_audiencecount'].replace(['Link error'],np.nan)
    df['mc_audiencecount'] = df['mc_audiencecount'].replace(['tbd'],np.nan)
    df['mc_audiencescore'] = df['mc_audiencescore'].replace(['Link error'],np.nan)
    df['mc_audiencescore'] = df['mc_audiencescore'].replace(['tbd'],np.nan)
    df['mc_audiencescore'] = df['mc_audiencescore'].replace(['No score yet'],np.nan)

    df['imdbcount'] = imdb['imdbcount'].replace(',','', regex=True)
    df['mc_criticscore'] =pd.to_numeric(df['mc_criticscore'])*10
    df['mc_criticcount'] =pd.to_numeric(df['mc_criticcount'])
    df['mc_audiencescore'] =pd.to_numeric(df['mc_audiencescore'])*10
    df['mc_audiencecount'] =pd.to_numeric(df['mc_audiencecount'])
    df['imdbscore'] =pd.to_numeric(df['imdbscore'])

    mean_imdb = df['imdbscore'].mean()
    mean_metacritic_critic=df['mc_criticscore'].mean()

    df[df.duplicated(subset=['tomato_title'])].sort_values(by='mojo_title')
    df.dropna(subset=['tomato_title'])

    df['domestic_revenue'] = df['domestic_revenue'].str.replace(',', '')
    df['domestic_revenue'] = df['domestic_revenue'].str.replace('$', '')
    df['domestic_revenue'] = pd.to_numeric(df['domestic_revenue'])
    df['international_reveneue'] = df['international_reveneue'].str.replace(',', '')
    df['international_reveneue'] = df['international_reveneue'].str.replace('$', '')
    df['international_reveneue'] = pd.to_numeric(df['international_reveneue'])
    df['world_revenue'] = df['world_revenue'].str.replace(',', '')
    df['world_revenue'] = df['world_revenue'].str.replace('$', '')
    df['world_revenue'] = pd.to_numeric(df['world_revenue'])
    df['opening_revenue'] = df['opening_revenue'].str.replace(',', '')
    df['opening_revenue'] = df['opening_revenue'].str.replace('$', '')
    df['opening_revenue'] = pd.to_numeric(df['opening_revenue'])

    df_new = df
    df_new = df_new.drop(columns=['domestic_revenue', 'international_reveneue', 'opening_revenue',
                                  'imdbpicture', 'imdb_metacritic', 'mc_criticscore', 'mc_criticcount',
                                'mc_audiencescore', 'mc_audiencecount', 'url', 'tomato_title',
                                'tomato_criticscore', 'tomato_audiencescore', 'tomato_criticcount',
                                'tomato_audiencecount', 'tomato_image'], axis=1)
    df_new = df_new.dropna(subset=['genres'])

    #add-in genres
    genres = np.unique(', '.join(df_new['genres']).split(', '))
    genres = np.delete(genres, np.where(genres == 'NA'))
    for genre in genres:
        df_new[genre] = df_new['genres'].str.contains(genre).astype('int')
    df_new.drop('genres', axis=1, inplace=True)

    target = df_new['imdbscore']
    features = df_new[['world_revenue', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary',
               'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery',
               'News', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']]
    distributors = df.distributor.value_counts()
    other_distributors = list(distributors[distributors <= 30].index)
    X5 = df_new.copy()
    X5 = pd.get_dummies(X5, columns=['distributor'])

    add_in_more_features = X5.iloc[:, 10:]
    more_features_list = add_in_more_features.columns.values.tolist()

    X5 = X5.dropna(subset=['imdbscore'])

    y = X5['imdbscore']
    lasso_model = Lasso(alpha = 0.01)
    lasso_model.fit(X5.loc[:,more_features_list], y)
    X5['pred'] = lasso_model.predict(X5.loc[:,more_features_list])

    df_final = df.merge(X5, on="mojo_title", how="right")
    df_final['pred'] = df_final['pred'].round(1)

    df_final = df_final.sort_values(by=['domestic_revenue'], ascending=False)
    df_final = df_final.dropna(subset=['tomato_image'])

    # max = df_final['pred'].max()
    # liams_favorite = df_final[df_final['pred'] == max]['mojo_title']
    # liams_favorite = liams_favorite.values

    html_data = df_final
    return html_data
