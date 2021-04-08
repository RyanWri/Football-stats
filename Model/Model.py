import os
import pandas as pd


class Model:
    def __init__(self):
        self.stats_csv_filename = 'all_teams_stats.csv'
        try:
            os.chdir('/Users/rywright/Football/Data')
            df = pd.read_csv(self.stats_csv_filename)
        except FileNotFoundError as e:
            print(e)

        self.df = df

    def highest_teams_to_draw(self):
        rate = 0.33
        data = self.df.loc[(self.df['draw_rate'] > rate) & (self.df['diff_goals'] < 25)]
        return data.sort_values(by=['streak'], ascending=False)


def main():
    model = Model()
    table = model.highest_teams_to_draw()
    table.to_csv('draw_teams.csv')


if __name__ == "__main__":
    main()