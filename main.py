from flask import Flask, request, render_template, session, redirect
import pandas as pd
from datetime import date
import os
from Model.Model import Model


app = Flask(__name__)


@app.route('/', methods=("POST", "GET"))
def index():
    today = date.today().strftime("%Y-%m-%d")
    filename = f'/Users/rywright/Football/Data/{today}-predictions.csv'
    if not os.path.isfile(filename):
        model = Model()
        df = model.draw_prediction_csv()
    else:
        df = pd.read_csv(filename)
    return render_template('index.html', arr=df.values)


if __name__ == '__main__':
    app.run(debug=True)