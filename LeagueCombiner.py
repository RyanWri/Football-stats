'''
    LeagueCombiner module built to answer the following questions:
        1) Top Team to Draw
        2) Top Team to Lose
        3) Top Team to Win
        4) Top Scoring Team
        5) Lowest Scoring Team
        6) Top Conceding Team
        7) Lowest Conceding Team
        8) Team with Longest losing streak and actual number
        9) Team with Longest winning streak and actual number
        10) Team with Longest drawing streak and actual number
        11) Team with Longest streak without draw and actual number
'''

import pandas as pd
import os
from collections import Counter


class LeagueCombiner:
    def __init__(self, leaguedf):
        teams = set(leaguedf['home-team'].unique()).union(set(leaguedf['away-team'].unique()))
        self._df = leaguedf
        self._teams = list(teams)
        self._teamsdict = self.run_stats_on_league()


    def run_stats_on_league(self):
        teamsdict = dict()
        for team in self._teams:
            homedf = self._df[self._df['home-team'] == team]
            awaydf = self._df[self._df['away-team'] == team]
            outcomes1 = homedf['matchResults'].values
            outcomes2 = awaydf['matchResults'].values
            stats1, stats2 = Counter(outcomes1), Counter(outcomes2)
            won, draw, lost = stats1['1'] + stats2['2'], stats1['X'] + stats2['X'], stats1['2'] + stats2['1']
            played = won + draw + lost
            scored = sum(homedf['home-score'].astype(int)) + sum(awaydf['away-score'].astype(int))
            conceived = sum(homedf['away-score'].astype(int)) + sum(awaydf['away-score'].astype(int))
            teamsdict[team] = {'played': played, 'won': won, 'draw': draw, 'lost': lost,
                               'scored': scored, 'conceived': conceived}

        return teamsdict


    def dict_to_dataframe(self, title):
        df = pd.DataFrame.from_dict(self._teamsdict, orient='index')
        os.chdir('/Users/rywright/Football/LeaguesData')
        for col in df.columns:
            df[col] = df[col].astype(int)
        df['diff'] = df['scored'] - df['conceived']
        finaldf = df.sort_values(by='diff')
        finaldf.to_csv(f'{title}-stats.csv')


def main():
    filename = 'predictz-july2020-to-january2021.csv'
    title = 'England Championship'
    league = LeagueCombiner(filename, title)
    league.dict_to_dataframe(title)


if __name__ == "__main__":
    main()
