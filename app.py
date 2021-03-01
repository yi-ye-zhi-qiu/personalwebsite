#Import flask
from flask import *
from flask import Flask, render_template, request, jsonify, make_response

#import models
from models.liamometer import get_movie_data
from models.liam_gg import game_info_by_match_id

#import this for lieum.gg/liam.gg to work
from riotwatcher import LolWatcher, ApiError
import pandas as pd

#from models.liam_gg_ml import give_shap_plot

# import shap
# shap.initjs()
# import matplotlib
# matplotlib.use('qt5agg')

app = Flask(__name__)

#Home/landing page
@app.route('/')
def show_index():
    #just serve up index.html
    return render_template('index.html')

#Petrarch NLP project page
@app.route('/petrarch')
def show_petrarch():
    return render_template('petrarch.html')

#Petrarch tensor page
@app.route('/petrarchtensor')
def show_petrach_tensor():
    return render_template('template_projector_config.json')

#Lieum.gg SEARCH page
@app.route('/league')
def show_league():
    return render_template('league.html')

#Lieum.gg POST-SEARCH page
@app.route('/league', methods=["GET", "POST"])
def riot_api_call():
    #Check if post method, if so store username searched as "name" variable
    if request.method == 'POST':
        form = request.form
    for key in form:
        name = form[key]

    #Define requisite variables for riot api call
    api_key = '' #get one @ https://developer.riotgames.com/
    region = 'na1' #this is only functional right now for North American data (LoL has European, Chinese, etc. servers)
    watcher = LolWatcher(api_key)
    #Define the user using python wrapper RiotWatcher for League of Legends data
    user = watcher.summoner.by_name('na1', name)
    #Get matchlist of the user
    matches = watcher.match.matchlist_by_account(region, user['accountId'])

    #get most recent 10 games of that user and the relevant GameIDs
    #change to 20, 30 if you want to display more data on the page
    #You may run into an API limit error doing that, though
    game_ids = []
    for i in range(0,10):
        game_ids.append(matches['matches'][i]['gameId'])

    #Get the user's ranked stats
    ranked_info = game_info_by_match_id(api_key, name, region,
                                        game_ids[0]).rank_stats()
    ranked_info = pd.DataFrame(ranked_info)
    #If unranked just put "unranked"
    if ranked_info.empty:
        ranked_info = pd.DataFrame({'tier': ['unranked']})
    #Get lowercase value of stuff like DIAMONDI, DIAMONDII etc.
    rank_league = ranked_info['tier'].values[0].lower()
    #profile picture is going to be hamstercam for unranked or the ranked picture otherwise
    if rank_league == 'unranked':
        rank = "static/images/ranked-emblems/hamster_cam.jpeg"
    else:
        rank = "static/images/ranked-emblems/"+rank_league+".png"

    #Assemble dataframes for each GameID (1 api request per game)
    dfs = {}
    for gameid in game_ids:
        dfs[gameid] = game_info_by_match_id(api_key,
                                          name, region,
                                          gamemode, gameid).match_data()

    #Assemble SHAP plots for each GameID (this is revealed by the show stats button)
    shap_plots = {}
    for b in dfs:
         shap_plots[b] = 'shap plot goes here'#give_shap_plot(dfs[b], name)

    #serve up liam.gg.html, but pass all of our variables as needed by Django
    return render_template('public/liam.gg.html', rank=rank,
                                                  ranked_info=ranked_info,
                                                  game_ids = game_ids,
                                                  form = form,
                                                  dfs=dfs,
                                                  shap_plots = shap_plots,
                                                  name=name)

#Liamometer page
@app.route('/liamometer')
def show_liamometer():
    """
    Performs linear regression on scraped databases (IMDB, BoxOfficeMojo).
    Returns 500 rows, just because I do not want to overload the page (currently working on lazy-load in javascript, or loading as you scroll.)
    """
    max, liams_favorite, liams_favorite_movie_image, html_data = get_movie_data()

    return render_template('liamometer.html', max=max, liams_favorite_movie_image = liams_favorite_movie_image,
                            liams_favorite=liams_favorite, html_data = html_data)

if __name__ == '__main__':
    app.run()
