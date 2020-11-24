import pandas as pd
import numpy as np
import os


class AdvancedDraw:
    def __init__(self, dataFilenmae):
        os.chdir('/Users/rywright/Football/Data')
        df = pd.read_csv( dataFilenmae )
        self.data = df.sort_values(['year', 'month', 'day'], ascending= [False, False, False] )
        self.teams = np.load('soccer-base-teams.npy')
        os.chdir('..')


    def calc_draw_rate_in_window( self, outcomes):
        streak = 0
        trueFreq = []
        for out in outcomes:
            if not out and streak > 0:
                trueFreq.append(streak)
            elif not out:
                streak = 0
            else:
                streak += 1

        if streak > 0:
            trueFreq.append(streak)

        return round( np.mean( trueFreq ), 7 )


    def calc_streak(self, outcomes):
        streak = 0
        for out in outcomes:
            if not out:
                break
            streak += 1

        return streak


    def calc_team_stats(self, team):
        result = []
        df = self.data
        records = df.loc[ (df['homeTeam'] == team) | (df['awayTeam'] == team) ].copy()
        outcomes = records['matchResults'].to_numpy(dtype='int')
        print(outcomes)

        result.append( self.calc_draw_rate_in_window( outcomes) )
        result.append( self.calc_streak(outcomes) )

        stats = np.array( result )
        return stats


    def frequent_teams_to_draw_csv(self):
        records = dict()
        for team in self.teams:
            records[team] = self.calc_team_stats( team )

        cols = 'draw rate|current streak'
        df = pd.DataFrame.from_dict( records, orient='index', columns = cols.split('|') )
        for col in df.columns:
            df[col] = df[col].astype(np.float)
        df['streakToDraw'] = df['current streak'] / df['draw rate']
        finaldf = df.loc[ df['streakToDraw'] >= 2.1]
        finaldf.to_csv('soccer-base-high-frequency-teams.csv')

    
def main():
    # soccer base stats
    soccerFilenmae = 'clean-soccerbase-total-data.csv'
    soccerbase = AdvancedDraw( soccerFilenmae )
    soccerbase.frequent_teams_to_draw_csv()

if __name__ == "__main__":
    main()