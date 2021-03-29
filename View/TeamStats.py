import os
import pandas as pd


class TeamStats:
    def __init__(self, team_name):
        os.chdir('/Users/rywright/Football/Data')
        df = pd.read_csv('combined_csv.csv')
        self.home_df = df.loc[df['home-team'] == team_name].copy()
        self.away_df = df.loc[df['away-team'] == team_name].copy()
        os.chdir('/Users/rywright/Football/View')

    @property
    def home(self):
        return self.home_df

    @property
    def away(self):
        return self.away_df


def main():
    team_name = 'Arsenal'
    team_stats = TeamStats(team_name)
    print(team_stats.home)
    print(team_stats.away)


if __name__ == '__main__':
    main()
