import os
import pandas as pd
import glob
import numpy as np


class TeamStats:
    def __init__(self):
        os.chdir('/Users/rywright/Football/Data')
        filename = 'clean-total-data.csv'
        if not os.path.isfile(filename):
            self.concat_and_write_csv_files(filename)
        self.df = pd.read_csv(filename)

    @staticmethod
    def concat_and_write_csv_files(filename):
        # change directory to concatenate all csv files
        os.chdir('/Users/rywright/Football/CsvData')

        extension = 'csv'
        all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
        # combine all files in the list
        combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])

        # change directory to Data and write csv
        os.chdir('/Users/rywright/Football/Data')
        combined_csv.to_csv(filename, index=False, encoding='utf-8-sig')

    def calc_team_stats(self, team_name):
        df = self.loc_team_raw_data(team_name)

        scored = np.sum(df.loc[df['home-team'] == team_name]['home-goals'])
        scored += np.sum(df.loc[df['away-team'] == team_name]['away-goals'])

        conceived = np.sum(df.loc[df['home-team'] == team_name]['away-goals'])
        conceived += np.sum(df.loc[df['away-team'] == team_name]['home-goals'])

        # we want the difference to be as close to 0 as possible
        diff_goals = abs(scored - conceived)

        # count consecutive games without draw
        streak = 0
        for outcome in df['draw'].values:
            if outcome > 0:
                break
            else:
                streak += 1

        draw_rate = round(np.sum(df['draw']) / len(df['home-goals']), 5)
        team_dict = {'streak': streak, 'draw_rate': draw_rate, 'diff_goals': diff_goals}

        return team_dict

    def calculate_draw_fixture(self,home_team, away_team):
        home_stats = self.calc_team_stats(home_team)
        away_stats = self.calc_team_stats(away_team)
        return home_stats,away_stats

    def loc_team_raw_data(self, team_name):
        data = self.df.loc[(self.df['home-team'] == team_name) | (self.df['away-team'] == team_name)].copy()
        return data.sort_values(by="formatted-date", ascending=False)


def main():
    t = TeamStats()


if __name__ == '__main__':
    main()
