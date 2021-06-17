import os
import pandas as pd
import numpy as np

class ModelDraw:
    def __init__(self):
        self.stats_csv_filename = 'all_teams_stats.csv'
        try:
            os.chdir('/Users/rywright/Football/Data')
            df = pd.read_csv(self.stats_csv_filename, index_col=0)
        except FileNotFoundError as e:
            print(e)
        self.df = df

    def top_teams_to_draw(self, threshold=0.3, num_of_games=50, home_flag=True):
        fixture = 'home' if home_flag else 'away'
        teams = []
        for team in self.df.index:
            draw = self.df.loc[team][fixture + '-draws']
            played = self.df.loc[team][fixture + '-played']
            val = draw / played if played > num_of_games else 0
            if val >= threshold:
                teams.append(team)

        return teams

    def print_teams_stats(self, teams, home_flag=True):
        fixture = 'home' if home_flag else 'away'
        print(self.df.loc[teams][[fixture + '-draws', fixture + '-played']])
        return 1


def main():
    model = ModelDraw()
    threshold = 0.33
    num_of_games = 60
    teams = model.top_teams_to_draw(threshold, num_of_games, home_flag=False)
    model.print_teams_stats(teams, home_flag=False)


if __name__ == "__main__":
    main()
