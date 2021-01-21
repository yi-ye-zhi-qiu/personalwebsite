from flask import *
import pandas as pd
import re

app = Flask(__name__)

@app.route('/mangodb')
def showMango():

    #Read in csvs and set index
    mojo = pd.read_csv('.data/mojo_revised.csv')
    imdb = pd.read_csv('.data/imdb.csv')
    metacritic = pd.read_csv('.data/metacritic.csv')
    tomato = pd.read_csv('.data/rotten_tomatoes.csv')
    heirloom = pd.read_csv('.data/heirloom.csv')
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
    df = df.dropna(subset=['tomato_criticscore'])
    df = df.dropna(subset=['mc_criticscore'])
    df = df.dropna(subset=['imdbscore'])
    df = df[df.imdbscore != 'Link error']
    df = df[df.mc_criticscore != 'Link error']
    df = df[df.mc_criticscore != 'tbd']
    df = df[df.mc_criticscore != 'No score yet']
    df = df[df.mc_audiencescore != 'No score yet']
    df.drop_duplicates(subset=['tomato_title'], inplace=True)
    df['domestic_revenue'] = df['domestic_revenue'].str.replace(',', '')
    df['domestic_revenue'] = df['domestic_revenue'].str.replace('$', '')
    df['domestic_revenue'] = pd.to_numeric(df['domestic_revenue'])
    df = df.sort_values(by=['domestic_revenue'], ascending=False)
    html_data = df.head(50)
    return render_template('mangodb.html', html_data = html_data)

@app.route('/aboutme')
def showAbout():
    return render_template('aboutme.html')

@app.route('/portfolio')
def showPortfolio():
    return render_template('portfolio.html')

@app.route('/')
def showIndex():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
