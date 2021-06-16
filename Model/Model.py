import os
import pandas as pd
from View.Crawler import Crawler
from datetime import date
import numpy as np


class Model:
    def __init__(self):
        self.today_date = date.today().strftime("%Y-%m-%d")
        self.stats_csv_filename = 'all_teams_stats.csv'
        try:
            os.chdir('/Users/rywright/Football/Data')
            df = pd.read_csv(self.stats_csv_filename, index_col=0)
        except FileNotFoundError as e:
            print(e)
        self.crawler = Crawler()
        self.df = df

    def crawl_and_save_fixtures(self):
        fixtures = ''

        today_data = self.crawler.get_matches_as_bs4_from_url(self.today_date)
        home_teams = np.array(today_data['team homeTeam'])
        away_teams = np.array(today_data['team awayTeam'])

        for h,a in zip(home_teams, away_teams):
            # match delimiter is --vs--
            # fixtures delimiter is ||
            fixtures += f'{h}--vs--{a}||'

        with open(f'fixtures-{self.today_date}.txt', 'w') as text_file:
            print(fixtures, file=text_file)

        return fixtures.split('||')[:-1]

    def load_fixtures(self):
        os.chdir('/Users/rywright/Football/Data')
        with open(f'fixtures-{self.today_date}.txt', 'r') as text_file:
            fixtures = text_file.read()

        # last match is \n
        return fixtures.split('||')[:-1]

    def calculate_prediction(self, home_team, away_team):
        index_teams = self.df.index
        prediction = []
        if home_team not in index_teams or away_team not in index_teams:
            return prediction

        home_stats, away_stats = self.df.loc[home_team], self.df.loc[away_team]

        # draw stats
        played = home_stats['home-played'] + away_stats['away-played']
        win = home_stats['home-wins'] + away_stats['away-losses']
        draw = home_stats['home-draws'] + away_stats['away-draws']
        lost = home_stats['home-losses'] + away_stats['away-wins']

        prediction = [home_team, away_team, win / played, draw / played, lost / played]
        return np.array(prediction)

    def create_predictions_dataframe(self):
        if not os.path.isfile(f'fixtures-{self.today_date}.txt'):
            fixtures = self.crawl_and_save_fixtures()
        else:
            fixtures = self.load_fixtures()

        predictions = []
        for match in fixtures:
            teams = match.split('--vs--')
            h, a = teams[0], teams[1]
            prediction = self.calculate_prediction(h, a)
            # append only if team exist in index
            if len(prediction) > 0:
                predictions.append(prediction)

        # we want prediction to be highest as possible
        cols = ['home-team', 'away-team', '1', 'X', '2']
        data = pd.DataFrame(predictions, columns=cols)
        return data

    def write_predictions_csv(self):
        data = self.create_predictions_dataframe()
        # write csv
        data.to_csv(f'extended-{self.today_date}-predictions.csv', index=False)


def main():
    model = Model()
    model.write_predictions_csv()


if __name__ == "__main__":
    main()
