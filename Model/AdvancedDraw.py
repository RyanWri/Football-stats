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
        counts = outcomes.value_counts().to_dict()
        draw = 0 if 0 not in counts.keys() else counts[0]
        numerator = draw / len(outcomes) if len(outcomes) > 0 else 0
        return round( numerator, 8 )


    def calc_streak(self, outcomes):
        streak = 0
        for out in outcomes:
            if abs(out) > 0:
                streak += 1
            else:
                break

        return streak


    def calc_team_stats(self, team):
        df = self.data
        records = df.loc[ (df['homeTeam'] == team) | (df['awayTeam'] == team) ].copy()
        result = []
        outcomes = records['matchResults'].astype(np.int)
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
        df['streak*rate'] = df['draw rate'] * df['current streak']

        likelyDf = self.most_likely_to_draw(df)
        likelyDf.to_csv('soccer-base-high-frequency-teams.csv')


    def most_likely_to_draw(self, df):
        df['streak*rate'] = df['streak*rate'].astype(np.float)
        return df.loc[ df['streak*rate'] > 2 ]

    
def main():
    # soccer base stats
    soccerFilenmae = 'clean-soccerbase-total-data.csv'
    soccerbase = AdvancedDraw( soccerFilenmae )
    soccerbase.frequent_teams_to_draw_csv()


if __name__ == "__main__":
    main()