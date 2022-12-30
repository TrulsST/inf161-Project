from flask import Flask, request, render_template
from waitress import serve
import pandas as pd
import pickle

games_2020 = pd.read_csv("test_data_games.csv")
model = pickle.load(open('model.pkl', 'rb'))

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('./index.html')

@app.route('/predict', methods=['post'])
def predict():
    # get data
    teams = dict(request.form)
    features = ['HomeGround', 'AvgGoalsScored_90', 'GlsRatio', '%FPla', 'Avg_Age', 'OppGlsAgst90', 'tablePos', 'points']
    home_team = teams['Home Team']
    away_team = teams['Away Team']
    if home_team == away_team:
        return render_template(
        './index.html',
        prediction_text=f'The home- and away-team is the same, no prediction availible.')
    teams_from_file = games_2020["Team"].unique()
    print(teams_from_file)
    if home_team not in teams_from_file:
        return render_template(
        './index.html',
        prediction_text=f'The team {home_team} is not playing in the league for 2020.')
    if away_team not in teams_from_file:
        return render_template(
        './index.html',
        prediction_text=f'The team {away_team} is not playing in the league for 2020.')
    ## Locate where team equals home_team, and opponent equals away_team and where homeground equals 1 (Indicating we have the row with the home teams info for the right match)
    ## Locate where team equals away_team, and opponent equals home_team and where homeground equals 0 (Indicating we have the row with the away teams info for the right match)

    home_game_data = games_2020.loc[(games_2020["Team"] == home_team) & (games_2020["Opponent"] == away_team) & (games_2020["HomeGround"] == 1)]
    away_game_data = games_2020.loc[(games_2020["Team"] == away_team) & (games_2020["Opponent"] == home_team) & (games_2020["HomeGround"] == 0)]

    X_home = home_game_data[features]
    X_away = away_game_data[features]
    print(X_home)
    print(X_away)
    score_home_team = round(model.predict(X_home)[0])
    score_away_team = round(model.predict(X_away)[0])
    
    # render with new prediction_text
    return render_template(
        './index.html',
        prediction_text=f'Predicted Score: \n{home_team} {score_home_team} - {score_away_team} {away_team}')

if __name__ == '__main__':
    print("name == main")
    app.run(host='localhost', port=8080,debug=True)
    serve(app)
