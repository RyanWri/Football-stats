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


    def calc_draw_rate_in_window( self, outcomes, size):
        counts = outcomes.value_counts().to_dict()
        draw = 0 if 0 not in counts.keys() else counts[0]
        numerator = draw / size
        return round( numerator, 7 )


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
        records = df.loc[ (df['homeTeam'] == team) | (df['awayTeam'] == team) ]
        if len( records ) < 30:
            # all games draw | six games draw | nine  games draw | tweleve games draw | current streak
            stats = np.zeros( 5 )
        else:
            outcomes = records['matchResults'].astype( np.int )
            result = []
            for games in [len(outcomes), 6, 12, 18]:
                result.append( self.calc_draw_rate_in_window( outcomes[:games], games) )
            result.append( self.calc_streak(outcomes) )
            stats = np.array( result )

        return stats


    def frequent_teams_to_draw_csv(self):
        records = dict()
        for team in self.teams:
            records[team] = self.calc_team_stats( team )

        cols = 'all games draw|six games draw|tweleve games draw|eighteen games draw|current streak'
        df = pd.DataFrame.from_dict( records, orient='index', columns = cols.split('|') )

        reldf = self.high_value_teams( df )
        reldf.to_csv('soccer-base-high-frequency-teams.csv')


    def high_value_teams(self, df):
        for col in df.columns:
            df[col] = df[col].astype( np.float )

        relDf = df.loc[ (df['all games draw'] >= 0.25) & (df['six games draw'] >= 0.1666)
                        & (df['tweleve games draw'] >= 0.1666) & (df['eighteen games draw'] >= 0.1666 )
                        &(df['current streak'] >= 3.0) ]

        return relDf

    
def main():
    # soccer base stats
    soccerFilenmae = 'clean-soccerbase-total-data.csv'
    soccerbase = AdvancedDraw( soccerFilenmae )
    soccerbase.frequent_teams_to_draw_csv()


if __name__ == "__main__":
    main()