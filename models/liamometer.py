from flask import *
import pandas as pd
import re
import numpy as np
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression, Lasso, LassoCV, Ridge, RidgeCV

def get_movie_data():

    #read in data
    #mojo = BoxOfficeMojo
    mojo = pd.read_csv('/Users/liamisaacs/Desktop/github repositories/personalwebsite/data/mojo.csv')
    #mojo = pd.read_csv('/var/www/liamisaacs/data/mojo.csv')
    mojo.set_index(['mojo_title'])
    #imdb = IMDb
    imdb = pd.read_csv('/Users/liamisaacs/Desktop/github repositories/personalwebsite/data/imdb.csv')
    #imdb = pd.read_csv('/var/www/liamisaacs/data/imdb.csv')
    imdb.set_index(['mojo_title'])
    #movie images are from RottenTomatoes
    #movie_images = pd.read_csv('/var/www/liamisaacs/data/heirloom.csv')
    movie_images = pd.read_csv('/Users/liamisaacs/Desktop/github repositories/personalwebsite/data/heirloom.csv')
    movie_images.set_index(['mojo_title'])
    movie_images.dropna(subset=['tomato_image'], inplace=True)
    movie_images.drop(columns=['url', 'tomato_criticcount', 'tomato_audiencecount'], inplace=True)

    def get_img_url(df):
        return re.findall('(?<=data-src).*$', df)[0][2:-2]
    movie_images['tomato_image'] = movie_images['tomato_image'].apply(get_img_url)

    imdb = imdb.drop(imdb[imdb['imdbscore']=='Link error'].index)
    imdb['imdbscore'] = pd.to_numeric(imdb['imdbscore'])
    #keep only relevant columns
    df = mojo.merge(imdb, on='mojo_title', how='left')
    df.drop(columns=['budget', 'MPAA', 'imdbpicture', 'imdbcount', 'imdb_metacritic', 'release_days', 'opening_theaters'], inplace=True)
    df = df.dropna(subset=['imdbscore'])
    #drop duplicates
    df.drop_duplicates(subset=['mojo_title'], inplace=True)

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

    lasso_cv_5_fold = LassoCV(cv=5)
    lasso_cv_5_fold.fit(X_3_scaled, y)
    pred_lasso = lasso_cv_5_fold.predict(X_3_scaled)

    # final_model = LinearRegression()
    # final_model.fit(X_3_scaled, y)
    # final_model_predicted_imdb_score = final_model.predict(X_3_scaled)

    X_3['pred'] = pred_lasso

    df_merge_this = df.drop(columns=df.iloc[:,2:7])
    df_merge_this = df_merge_this.drop(columns=['domestic_international_ratio'])

    df_final = df_merge_this.merge(X_3, right_index=True, left_index=True)

    df_final = df_final.merge(movie_images, on='mojo_title', how='inner')

    df_final = df_final.sort_values(by=['pred'], ascending=False)
    #only display what we have images for
    df_final = df_final.dropna(subset=['tomato_image'])
    df_final['pred'] = df_final['pred'].round(1)

    max = df_final['pred'].max()
    liams_favorite = df_final[df_final['pred'] == max]['mojo_title']
    liams_favorite = liams_favorite.values
    liams_favorite_movie_image = 'https://m.media-amazon.com/images/M/MV5BYjQ5NjM0Y2YtNjZkNC00ZDhkLWJjMWItN2QyNzFkMDE3ZjAxXkEyXkFqcGdeQXVyODIxMzk5NjA@._V1_UY268_CR3,0,182,268_AL_.jpg'
    # IT JUST SO HAPPENS the one image for Coco is somehow directly to the wrong image on rottentomatoes,
    # so instead of df_final[df_final['mojo_title'] == liams_favorite[0]]['tomato_image']
    # we have to manually fix it

    html_data = df_final
    return max, liams_favorite, liams_favorite_movie_image, html_data
