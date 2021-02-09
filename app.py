from flask import *
from flask import Flask, render_template, request, jsonify, make_response
from models.liamometer import get_movie_data
from riotwatcher import LolWatcher, ApiError
from models.liam_gg import game_info_by_match_id
import pandas as pd

app = Flask(__name__)

@app.route('/liamometer')
def show_mango():
    """
    Performs linear regression on scraped databases (rottentomatoes, metacritic, IMDB, BoxOfficeMojo),
    takes in these 5 CSVs.
    Returns 1500 rows, just because I do not want to overload the page (currently working on lazy-load in javascript, or loading as you scroll.)
    """
    max, liams_favorite, liams_favorite_movie_image, html_data = get_movie_data()


    return render_template('liamometer.html', max=max, liams_favorite_movie_image = liams_favorite_movie_image,
                            liams_favorite=liams_favorite, html_data = html_data)
#
# @app.route("/load")
# def load():
#     """ Route to return the posts """
#
#     time.sleep(0.2)  # Used to simulate delay
#
#     if request.args:
#         counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
#
#         if counter == 0:
#             print(f"Returning posts 0 to {quantity}")
#             # Slice 0 -> quantity from the db
#             res = make_response(jsonify(db[0: quantity]), 200)
#
#         elif counter == posts:
#             print("No more posts")
#             res = make_response(jsonify({}), 200)
#
#         else:
#             print(f"Returning posts {counter} to {counter + quantity}")
#             # Slice counter -> quantity from the db
#             res = make_response(jsonify(db[counter: counter + quantity]), 200)
#
#     return res

@app.route('/')
def show_index():
    return render_template('index.html')

@app.route('/portfolio')
def show_portfolio():
    return render_template('portfolio.html')

@app.route('/league')
def show_league():
    return render_template('league.html')

@app.route('/league', methods=["GET", "POST"])
def riot_api_call():
    if request.method == 'POST':
        form = request.form
    for key in form:
        name = form[key]
    #define as static variables for now, must be updated via form info
    api_key = ''
    gamemode = 'CLASSIC'
    region = 'na1'

    watcher = LolWatcher(api_key)
    user = watcher.summoner.by_name('na1', name)
    matches = watcher.match.matchlist_by_account(region, user['accountId'])

    game_ids = []

    for i in range(0,2): #display 10 games
        game_ids.append(matches['matches'][i]['gameId'])

    ranked_info = game_info_by_match_id(api_key, name, region,
                                        gamemode, game_ids[0]).rank_stats()
    ranked_info = pd.DataFrame(ranked_info)
    if ranked_info.empty:
        ranked_info = pd.DataFrame({'tier': ['unranked']})

    rank_league = ranked_info['tier'].values[0].lower()
    if rank_league == 'unranked':
        rank = "/static/images/ranked-emblems/hamster_cam.jpeg"
    else:
        rank = "/static/images/ranked-emblems/"+rank_league+".png"

    dfs = {}
    for gameid in game_ids:
        dfs[gameid] = game_info_by_match_id(api_key,
                                          name, region,
                                          gamemode, gameid).match_data()

    return render_template('public/liam.gg.html', rank=rank, ranked_info=ranked_info, game_ids = game_ids, form = form, dfs=dfs, name=name)

if __name__ == '__main__':
    app.run()
