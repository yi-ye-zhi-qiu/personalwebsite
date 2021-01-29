from flask import *
from flask import Flask, render_template, request, jsonify, make_response

from python_data_apps.movies_db import get_movie_data

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

@app.route("/riot-api-form", methods=["GET", "POST"])
def riot_api_call():
    return render_template('public/league.html')

if __name__ == '__main__':
    app.run()
