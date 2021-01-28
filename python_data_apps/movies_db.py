from flask import *
import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures, OneHotEncoder
from sklearn.linear_model import LinearRegression, Lasso, LassoCV, Ridge, RidgeCV
from sklearn.metrics import r2_score

def get_movie_data():

    #read in data
    #mojo = BoxOfficeMojo
    mojo = pd.read_csv('data/mojo.csv')
    mojo.set_index(['mojo_title'])
    #imdb = IMDb
    imdb = pd.read_csv('data/imdb.csv')
    imdb.set_index(['mojo_title'])
    #movie images are from RottenTomatoes
    movie_images = pd.read_csv('data/heirloom.csv')
    movie_images.set_index(['mojo_title'])

    imdb = imdb.drop(imdb[imdb['imdbscore']=='Link error'].index)
    imdb['imdbscore'] = pd.to_numeric(imdb['imdbscore'])

    #keep only relevant columns
    df = mojo.merge(imdb, on='mojo_title', how='left')
    df.drop(columns=['budget', 'MPAA', 'imdbpicture', 'imdbcount', 'imdb_metacritic', 'release_days', 'opening_theaters'], inplace=True)
    df = df.dropna(subset=['imdbscore'])

    #revisions to $2,000 to now be 2000
    df['domestic_revenue'] = df['domestic_revenue'].str.replace(',', '')
    df['domestic_revenue'] = df['domestic_revenue'].str.replace('$', '')
    df['domestic_revenue'] = pd.to_numeric(df['domestic_revenue'])
    df['international_revenue'] = df['international_revenue'].str.replace(',', '')
    df['international_revenue'] = df['international_revenue'].str.replace('$', '')
    df['international_revenue'] = pd.to_numeric(df['international_revenue'])
    df['world_revenue'] = df['world_revenue'].str.replace(',', '')
    df['world_revenue'] = df['world_revenue'].str.replace('$', '')
    df['world_revenue'] = pd.to_numeric(df['world_revenue'])
    df['opening_revenue'] = df['opening_revenue'].str.replace(',', '')
    df['opening_revenue'] = df['opening_revenue'].str.replace('$', '')
    df['opening_revenue'] = pd.to_numeric(df['opening_revenue'])

    #create a new df with just imdb score and world revenue, domestic_international_ratio
    df_new = df
    df['domestic_international_ratio'] = df['domestic_revenue'] / df['international_revenue']
    df_new = df_new.drop(columns=['mojo_title', 'international_revenue', 'domestic_revenue',
                                 'opening_revenue'], axis=1)

    df_new = df_new.dropna(subset=['genres'])

    #one-hot-encode genre
    genres = np.unique(', '.join(df_new['genres']).split(', '))
    genres = np.delete(genres, np.where(genres == 'NA'))
    for genre in genres:
        df_new[genre] = df_new['genres'].str.contains(genre).astype('int')
    df_new.drop('genres', axis=1, inplace=True)

    #hold 20% for final testing
    X, y = df_new, df_new['imdbscore']

    pd.to_numeric(X.iloc[:, 2].fillna(0))

    scaler = preprocessing.StandardScaler()
    X_scaled = scaler.fit_transform(X.iloc[:, 4:])

    #create genre-genre interactions

    def create_interactions(df):
        df_int = df.copy()
        for i in range(3, len(df.columns)-1):
            for j in range(i+1, len(df.columns)):
                name = str(df.columns[i]) + ' * ' + str(df.columns[j])
                df_int.loc[:, name] = df[str(df.columns[i+1])] * df[str(df.columns[j])]
        return df_int

    X_interactions = create_interactions(X)
    X_interactions.drop(columns=['distributor'], axis=1)
    X_interactions = X_interactions.drop(columns=['imdbscore'])
    X_interactions = X_interactions.iloc[:, 3:380]

    X['domestic_international_ratio'].fillna(value=0, inplace=True)

    X_2 = X.merge(X_interactions.iloc[:, 26:380], how='inner', left_index=True, right_index=True)
    #^^ merge back in our interactions

    #set distributor to Other if movies <=10/yr

    distributors = df.distributor.value_counts()
    other_distributors = list(distributors[distributors <= 40].index)
    X_2['distributor'] = X_2['distributor'].replace(other_distributors, 'Other')

    #one-hot-encode distributor

    X_3 = X_2.copy()
    X_3 = pd.get_dummies(X_3, columns=['distributor'], drop_first=True)

    X_3 = X_3.drop(columns=['imdbscore'])

    X_3_scaled = scaler.fit_transform(X_3)
    final_model = LinearRegression()
    final_model.fit(X_3_scaled, y)
    final_model_predicted_imdb_score = final_model.predict(X_3_scaled)

    X_3['pred'] = final_model_predicted_imdb_score

    df_merge_this = df.drop(columns=df.iloc[:,2:7])
    df_merge_this = df_merge_this.drop(columns=['domestic_international_ratio'])

    df_final = df_merge_this.merge(X_3, right_index=True, left_index=True)

    movie_images.drop(columns=['url', 'tomato_criticcount', 'tomato_audiencecount'], inplace=True)


    df_final = df_final.merge(movie_images, on='mojo_title', how='right')

    df_final = df_final.sort_values(by=['domestic_revenue'], ascending=False)
    #only display what we have images for
    df_final = df_final.dropna(subset=['tomato_image'])

    html_data = df_final
    return html_data

    # X5['pred'] = lasso_model.predict(X5.loc[:,more_features_list])
    #
    # df_final = df.merge(X5, on="mojo_title", how="right")
    # df_final['pred'] = df_final['pred'].round(1)
    #
    # df_final = df_final.sort_values(by=['domestic_revenue'], ascending=False)
    # df_final = df_final.dropna(subset=['tomato_image'])

    # #Read in csvs and set index
    # mojo = pd.read_csv('data/mojo_revised.csv')
    # imdb = pd.read_csv('data/imdb.csv')
    # metacritic = pd.read_csv('data/metacritic.csv')
    # tomato = pd.read_csv('data/rotten_tomatoes.csv')
    # heirloom = pd.read_csv('data/heirloom.csv')
    # mojo.rename(columns={"title": "mojo_title"}, inplace=True)
    # heirloom.set_index(['mojo_title'])
    # mojo.set_index(['mojo_title'])
    # imdb.set_index(['mojo_title'])
    # metacritic.set_index(['mojo_title'])
    # tomato.set_index(['mojo_title'])
    #
    # tomato_final = tomato.merge(heirloom, on='mojo_title', how='left')
    # tomato_final = tomato_final.drop(['url_y', 'tomato_criticcount_x'], axis=1)
    # tomato_final = tomato_final.rename(columns={"tomato_criticcount_y":"tomato_criticcount", "url_x":"url"})
    # tomato_final = tomato_final.dropna(subset=['tomato_image'])
    #
    # def get_img_url(df):
    #     return re.findall('(?<=data-src).*$', df)[0][2:-2]
    # tomato_final['tomato_image'] = tomato_final['tomato_image'].apply(get_img_url)
    #
    # mojo['release_year'] = [x.strip()[-4:] for x in mojo['release_days'].astype(str)]
    #
    # mojo.drop_duplicates(subset='mojo_title', inplace=True)
    # imdb.drop_duplicates(subset='mojo_title', inplace=True)
    # df1 = mojo.merge(imdb, on='mojo_title', how='left')
    # metacritic.drop_duplicates(subset='mojo_title', inplace=True)
    # df2 = df1.merge(metacritic, on='mojo_title', how='left')
    # tomato_final.drop_duplicates(subset='mojo_title', inplace=True)
    #
    # df = df2.merge(tomato_final, on='mojo_title', how='left')
    #
    # df['tomato_audiencescore'] =pd.to_numeric(df['tomato_audiencescore'])
    # df['tomato_criticscore'] =pd.to_numeric(df['tomato_criticscore'])
    # df['tomato_criticscore'].fillna(df['tomato_criticscore'].mean())
    # df['tomato_audiencescore'].fillna(df['tomato_audiencescore'].mean())
    # df['tomato_title'].fillna(df['mojo_title'])
    # df[df['imdbscore'] == 'Link error'] = np.nan
    #
    # df['mc_criticscore'].isnull().sum(axis=0)
    #
    # df['mc_criticscore'] = df['mc_criticscore'].replace(['Link error'],np.nan)
    # df['mc_criticscore'] = df['mc_criticscore'].replace(['tbd'],np.nan)
    # df['mc_criticscore'] = df['mc_criticscore'].replace(['No score yet'],np.nan)
    # df['mc_criticcount'] = df['mc_criticcount'].replace(['Link error'],np.nan)
    # df['mc_criticcount'] = df['mc_criticcount'].replace(['tbd'],np.nan)
    #
    # df['mc_audiencecount'] = df['mc_audiencecount'].replace(['Link error'],np.nan)
    # df['mc_audiencecount'] = df['mc_audiencecount'].replace(['tbd'],np.nan)
    # df['mc_audiencescore'] = df['mc_audiencescore'].replace(['Link error'],np.nan)
    # df['mc_audiencescore'] = df['mc_audiencescore'].replace(['tbd'],np.nan)
    # df['mc_audiencescore'] = df['mc_audiencescore'].replace(['No score yet'],np.nan)
    #
    # df['imdbcount'] = imdb['imdbcount'].replace(',','', regex=True)
    # df['mc_criticscore'] =pd.to_numeric(df['mc_criticscore'])*10
    # df['mc_criticcount'] =pd.to_numeric(df['mc_criticcount'])
    # df['mc_audiencescore'] =pd.to_numeric(df['mc_audiencescore'])*10
    # df['mc_audiencecount'] =pd.to_numeric(df['mc_audiencecount'])
    # df['imdbscore'] =pd.to_numeric(df['imdbscore'])
    #
    # mean_imdb = df['imdbscore'].mean()
    # mean_metacritic_critic=df['mc_criticscore'].mean()
    #
    # df[df.duplicated(subset=['tomato_title'])].sort_values(by='mojo_title')
    # df.dropna(subset=['tomato_title'])
    #
    # df['domestic_revenue'] = df['domestic_revenue'].str.replace(',', '')
    # df['domestic_revenue'] = df['domestic_revenue'].str.replace('$', '')
    # df['domestic_revenue'] = pd.to_numeric(df['domestic_revenue'])
    # df['international_reveneue'] = df['international_reveneue'].str.replace(',', '')
    # df['international_reveneue'] = df['international_reveneue'].str.replace('$', '')
    # df['international_reveneue'] = pd.to_numeric(df['international_reveneue'])
    # df['world_revenue'] = df['world_revenue'].str.replace(',', '')
    # df['world_revenue'] = df['world_revenue'].str.replace('$', '')
    # df['world_revenue'] = pd.to_numeric(df['world_revenue'])
    # df['opening_revenue'] = df['opening_revenue'].str.replace(',', '')
    # df['opening_revenue'] = df['opening_revenue'].str.replace('$', '')
    # df['opening_revenue'] = pd.to_numeric(df['opening_revenue'])
    #
    # df_new = df
    # df_new = df_new.drop(columns=['domestic_revenue', 'international_reveneue', 'opening_revenue',
    #                               'imdbpicture', 'imdb_metacritic', 'mc_criticscore', 'mc_criticcount',
    #                             'mc_audiencescore', 'mc_audiencecount', 'url', 'tomato_title',
    #                             'tomato_criticscore', 'tomato_audiencescore', 'tomato_criticcount',
    #                             'tomato_audiencecount', 'tomato_image'], axis=1)
    # df_new = df_new.dropna(subset=['genres'])
    #
    # #add-in genres
    # genres = np.unique(', '.join(df_new['genres']).split(', '))
    # genres = np.delete(genres, np.where(genres == 'NA'))
    # for genre in genres:
    #     df_new[genre] = df_new['genres'].str.contains(genre).astype('int')
    # df_new.drop('genres', axis=1, inplace=True)
    #
    # target = df_new['imdbscore']
    # features = df_new[['world_revenue', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary',
    #            'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery',
    #            'News', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']]
    # distributors = df.distributor.value_counts()
    # other_distributors = list(distributors[distributors <= 30].index)
    # X5 = df_new.copy()
    # X5 = pd.get_dummies(X5, columns=['distributor'])
    #
    # add_in_more_features = X5.iloc[:, 10:]
    # more_features_list = add_in_more_features.columns.values.tolist()
    #
    # X5 = X5.dropna(subset=['imdbscore'])
    #
    # y = X5['imdbscore']
    # lasso_model = Lasso(alpha = 0.01)
    # lasso_model.fit(X5.loc[:,more_features_list], y)
    # X5['pred'] = lasso_model.predict(X5.loc[:,more_features_list])
    #
    # df_final = df.merge(X5, on="mojo_title", how="right")
    # df_final['pred'] = df_final['pred'].round(1)
    #
    # df_final = df_final.sort_values(by=['domestic_revenue'], ascending=False)
    # df_final = df_final.dropna(subset=['tomato_image'])
    #
    # # max = df_final['pred'].max()
    # # liams_favorite = df_final[df_final['pred'] == max]['mojo_title']
    # # liams_favorite = liams_favorite.values
    #
    # html_data = df_final
    # return html_data
