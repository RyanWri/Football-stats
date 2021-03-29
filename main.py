from flask import Flask, request, render_template, session, redirect
import pandas as pd
from View.TeamStats import TeamStats

app = Flask(__name__)


@app.route('/', methods=("POST", "GET"))
def index():
    return render_template('index.html')


@app.route('/tables', methods=("POST", "GET"))
def show_tables():
    df = pd.read_csv('Data/combined_csv.csv')
    df = df[df['home-team'] == 'Arsenal']
    return render_template('simple.html', tables=[df.to_html(classes='data')])


@app.route('/team', methods=("POST", "GET"))
def show_team():
    team_name = 'Arsenal'
    team_stats = TeamStats(team_name)
    df = team_stats.home
    return render_template('teamStats.html', tables=[df.to_html(classes='data')])


@app.route('/dropdown', methods=['GET'])
def dropdown():
    df = pd.read_csv('Data/combined_csv.csv')
    teams = list( df['home-team'].unique())
    return render_template('dropdown.html', teams=teams)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)