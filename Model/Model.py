import pandas as pd
from LeagueCombiner import LeagueCombiner
import os


class Model:
    def __init__(self, filename):
        os.chdir('/Users/rywright/Football/Data')
        # read data
        self.df = pd.read_csv(filename, index_col='date')
        self._leagues = self.df['league'].unique()


    def write_league_stats(self):
        for title in self._leagues:
            leaguedf = self.df[self.df['league'] == title]
            league = LeagueCombiner(leaguedf)
            league.dict_to_dataframe(title)


    @property
    def leagues(self):
        return self._leagues

    
def main():
    filename = 'predictz-july2020-to-january2021.csv'
    model = Model(filename)
    # run leagues stats
    model.write_league_stats()
    print('success')


if __name__ == "__main__":
    main()