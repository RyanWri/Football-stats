import os
import pandas as pd
import glob
import numpy as np
import pickle


class TeamStats:
    def __init__(self):
        os.chdir("/Users/rywright/Football/Data")
        filename = "clean-total-data.csv"
        if not os.path.isfile(filename):
            self.concat_and_write_csv_files(filename)
        self.df = pd.read_csv(filename)
        # for team stats dictionairy
        self.pickle_filename = "teams_special_score.pkl"
        self.stats_csv_filename = "all_teams_stats.csv"

    @staticmethod
    def concat_and_write_csv_files(filename):
        # change directory to concatenate all csv files
        os.chdir("/Users/rywright/Football/CsvData")

        extension = "csv"
        all_filenames = [i for i in glob.glob("*.{}".format(extension))]
        # combine all files in the list
        combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])

        # change directory to Data and write csv
        os.chdir("/Users/rywright/Football/Data")
        combined_csv.to_csv(filename, index=False)

    def calc_team_stats(self, team_name):
        team_stats = dict()
        home_data = self.loc_team_raw_data(team_name)
        away_data = self.loc_team_raw_data(team_name, field="away")

        team_stats["home-stats"] = self.calc_stats_from_games(home_data, field="home")
        team_stats["away-stats"] = self.calc_stats_from_games(away_data, field="away")

        return team_stats

    @staticmethod
    def calc_stats_from_games(df, field="home"):
        played = len(df["home-goals"])
        if field == "home":
            scored, conceived = np.sum(df["home-goals"]), np.sum(df["away-goals"])
            wins, draws = np.sum(df["home-won"]), np.sum(df["draw"])
            losses = played - wins - draws
        else:
            scored, conceived = np.sum(df["away-goals"]), np.sum(df["home-goals"])
            wins, draws = np.sum(df["away-won"]), np.sum(df["draw"])
            losses = played - wins - draws

        return [wins, draws, losses, played, scored, conceived]

    def loc_team_raw_data(self, team_name, field="home"):
        """
        :param team_name: self explanatory
        :param field: home games or away games
        :return: loc from dataframe with games stats
        """
        col = field + "-team"
        data = self.df.loc[(self.df[col] == team_name)].copy()
        return data

    def save_all_teams_stats_to_pickle(self):
        data = dict()
        away_unique = set(self.df["away-team"].unique())
        home_unique = set(self.df["home-team"].unique())
        teams = list(home_unique.union(away_unique))
        for team in teams:
            data[team] = self.calc_team_stats(team)

        fp = open(self.pickle_filename, "wb")
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

    @staticmethod
    def write_team_full_stats(team_dict):
        values = np.concatenate([team_dict["home-stats"], team_dict["away-stats"]])
        return values

    def write_team_stats_to_csv(self):
        # team stats file name is in init
        full_stats = dict()
        teams_dict = self.load_all_teams_stats_from_pickle()[0]
        for team in teams_dict.keys():
            full_stats[team] = self.write_team_full_stats(teams_dict.get(team))

        cols = "home-wins|home-draws|home-losses|home-played|home-scored|home-conceived"
        cols += (
            "|away-wins|away-draws|away-losses|away-played|away-scored|away-conceived"
        )

        df = pd.DataFrame.from_dict(full_stats, orient="index", columns=cols.split("|"))
        df.to_csv(self.stats_csv_filename)


def main():
    t = TeamStats()
    # t.save_all_teams_stats_to_pickle()
    t.write_team_stats_to_csv()


if __name__ == "__main__":
    main()
