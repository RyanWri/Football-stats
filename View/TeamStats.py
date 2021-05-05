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
        combined_csv.to_csv(filename, index=False)

    def calc_team_stats(self, team_name):
        df = self.loc_team_raw_data(team_name)
        played = len(df['home-goals'])

        #calculate goals scored and conceived
        scored = np.sum(df.loc[df['home-team'] == team_name]['home-goals'])
        scored += np.sum(df.loc[df['away-team'] == team_name]['away-goals'])
        scored = round(scored / played, 6)
        conceived = np.sum(df.loc[df['home-team'] == team_name]['away-goals'])
        conceived += np.sum(df.loc[df['away-team'] == team_name]['home-goals'])
        conceived = round(conceived / played, 6)

        #calculate wins draws and losses
        wins = np.sum(df.loc[df['home-team'] == team_name]['home-won'])
        wins += np.sum(df.loc[df['away-team'] == team_name]['away-won'])
        draws = np.sum(df['draw'])
        losses = played - draws - wins

        return [wins, draws, losses, played, scored, conceived]

    def loc_team_raw_data(self, team_name):
        data = self.df.loc[(self.df['home-team'] == team_name) | (self.df['away-team'] == team_name)].copy()
        return data

    def save_all_teams_stats_to_pickle(self):
        data = dict()
        away_unique = set(self.df['away-team'].unique())
        home_unique = set(self.df['home-team'].unique())
        teams = list(home_unique.union(away_unique))
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
        cols = ['wins', 'draws', 'losses', 'played', 'scored', 'conceived']
        df = pd.DataFrame.from_dict(data[0], orient='index', columns=cols)
        df.to_csv(self.stats_csv_filename)


def main():
    t = TeamStats()
    t.save_all_teams_stats_to_pickle()
    t.write_team_stats_to_csv()


if __name__ == '__main__':
    main()
