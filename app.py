from flask import Flask, request, render_template, session, redirect
import pandas as pd
from datetime import date
import os
from Model.Model import Model


app = Flask(__name__)


@app.route('/', methods=("POST", "GET"))
def index():
    cols = ['home-team', 'away-team', '1', 'X', '2', '1-goals', '2-goals', '1-conceived', '2-conceived']
    today = date.today().strftime("%Y-%m-%d")
    filename = f'/Users/rywright/Football/Data/extended-{today}-predictions.csv'
    if not os.path.isfile(filename):
        model = Model()
        df = model.write_extended_csv()
    else:
        df = pd.read_csv(filename)
    return render_template('index.html', arr=df.values, columns=cols)


@app.route('/teams', methods=("POST", "GET"))
def show_teams_stats():
    df = pd.read_csv('/Users/rywright/Football/Data/all_teams_stats.csv', index_col=0)
    return render_template('teams.html', teams=df.index[:5])


if __name__ == '__main__':
    app.run(debug=True)