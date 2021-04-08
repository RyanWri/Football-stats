import os
import pandas as pd
import glob
import numpy as np
import pickle


class TeamStats:
    def __init__(self):
        os.chdir('/Users/rywright/Football/Data')
        filename = 'clean-total-data.csv'
        if not os.path.isfile(filename):
            self.concat_and_write_csv_files(filename)
        self.df = pd.read_csv(filename)
        # for team stats dictionairy
        self.pickle_filename = 'teams_special_score.pkl'
        self.stats_csv_filename = 'all_teams_stats.csv'

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
        played = len(df['home-goals'])
        # do not count teams with less than 50 matches (small sample does not count)
        if played < 50:
            return [0, 0, 0]

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

        draw_rate = round(np.sum(df['draw']) / played, 6)
        return [draw_rate, diff_goals, streak]

    def calculate_draw_fixture(self,home_team, away_team):
        home_team_special_score = self.calc_team_stats(home_team)
        away_team_special_score = self.calc_team_stats(away_team)
        fixture_special_score = (home_team_special_score + away_team_special_score) / 2
        return fixture_special_score

    def loc_team_raw_data(self, team_name):
        data = self.df.loc[(self.df['home-team'] == team_name) | (self.df['away-team'] == team_name)].copy()
        return data.sort_values(by="formatted-date", ascending=False)

    def save_all_teams_stats_to_pickle(self):
        data = dict()
        teams = list(self.df['home-team'].unique())
        for team in teams:
            data[team] = self.calc_team_stats(team)

        fp = open(self.pickle_filename, 'wb')
        pickle.dump(data, fp)

    def load_all_teams_stats_from_pickle(self):
        pickle_file = open(self.pickle_filename, "rb")
        objects = []
        while True:
            try:
                objects.append(pickle.load(pickle_file))
            except EOFError:
                break
        pickle_file.close()

        return objects

    def write_team_stats_to_csv(self):
        # team stats file name is in init
        data = self.load_all_teams_stats_from_pickle()
        df = pd.DataFrame.from_dict(data[0], orient='index', columns=['draw_rate', 'diff_goals', 'streak'])
        df.to_csv(self.stats_csv_filename)


def main():
    t = TeamStats()
    t.save_all_teams_stats_to_pickle()
    t.write_team_stats_to_csv()


if __name__ == '__main__':
    main()
