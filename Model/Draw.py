import pandas as pd
import numpy as np
import os
from collections import Counter


class Draw:
    def __init__(self, dataFilenmae):
        os.chdir('/Users/rywright/Football/Data')
        self.data = pd.read_csv(dataFilenmae, index_col=0)
        self.hometeams = np.load('soccer-base-home-teams.npy')
        self.awayteams = np.load('soccer-base-away-teams.npy')
        os.chdir('..')


    def calc_win_draw_lose(self, outcomes, direction=True):
        '''
        :param outcomes: array of matches history of single team , direction flag if it is the home team or away team
        :return: win probability , draw probability ,lose probability
        '''
        n = len(outcomes)
        c = Counter(outcomes)

        win = c['H'] if direction else c['A']
        lose = c['A'] if direction else c['H']
        draw = c['D']

        return np.array([win, draw, lose])


    def calc_fixture_stats(self, hometeam, awayteam):
        df = self.data

        records = df.loc[(df['homeTeam'] == hometeam)]
        outcomes = records['matchResults'].values
        homestats = self.calc_win_draw_lose(outcomes)

        records = df.loc[(df['awayTeam'] == awayteam)]
        outcomes = records['matchResults'].values
        awaystats = self.calc_win_draw_lose(outcomes, direction=False)

        return np.concatenate( (homestats, awaystats), axis=None)


    def daily_teams_prediction_to_csv(self):
        records = dict()
        for hometeam, awayteam in zip( self.hometeams, self.awayteams):
            key = f'{hometeam} vs {awayteam}'
            stats = self.calc_fixture_stats(hometeam, awayteam)
            records[key] = stats

        cols = 'HHWin|HHDraw|HHLose|AAWin|AADraw|AALose'
        df = pd.DataFrame.from_dict(records, orient='index', columns=cols.split('|'), dtype=np.int)

        # calc new draw rate
        total = df.sum(axis = 1, skipna = True)
        df['homeTeam to win'] = (df['HHWin'] + df['AALose']) / total
        df['homeTeam to draw'] = (df['HHDraw'] + df['AADraw']) / total
        df['homeTeam to lose'] = (df['HHLose'] + df['AAWin']) / total

        finaldf = df.loc[ (df['homeTeam to win'] >= 0.5) | (df['homeTeam to draw'] >= 0.5) | (df['homeTeam to lose'] >= 0.5) ]
        finaldf.to_csv('soccer-base-high-frequency-teams.csv')

    
def main():
    # soccer base stats
    soccerFilenmae = 'clean-soccerbase-string.csv'
    soccerbase = Draw(soccerFilenmae)
    soccerbase.daily_teams_prediction_to_csv()


if __name__ == "__main__":
    main()