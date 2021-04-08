from flask import Flask, request, render_template, session, redirect
import pandas as pd
from View.TeamStats import TeamStats
from Model.Model import Model

app = Flask(__name__)
global team_stats
team_stats = TeamStats()


@app.route('/', methods=("POST", "GET"))
def index():
    return render_template('index.html')


@app.route('/tables', methods=("POST", "GET"))
def show_tables():
    df = pd.read_csv('CsvData/combined_csv.csv')
    df = df[df['home-team'] == 'Arsenal']
    return render_template('simple.html', tables=[df.to_html(classes='data')])


@app.route('/my-draw-predictions', methods=("POST", "GET"))
def show_predictions():
    model = Model()
    df = model.highest_teams_to_draw()
    return render_template('draw.html', tables=[df.to_html(classes='data')])


@app.route('/team-stats', methods=("POST", "GET"))
def show_team():
    df = pd.read_csv('/Users/rywright/Football/Data/all_teams_stats.csv')
    return render_template('teamStats.html', tables=[df.to_html(classes='data')])


@app.route('/dropdown', methods=['GET'])
def dropdown():
    df = pd.read_csv('/Users/rywright/Football/Data/clean-total-data.csv')
    teams = list( df['home-team'].unique())[:20]
    return render_template('dropdown.html', teams=teams)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)