import pandas as pd
import os
import numpy as np


class Cleaner:
    def __init__(self, filename, mode = 'append'):
        os.chdir('../Data')

        if mode == 'append':
            oldDatafilename = 'clean-total-data.csv'
            df = pd.read_csv( filename , index_col=0)
            df.to_csv(oldDatafilename, mode='a', header = False)

        else: #clean
            df = pd.read_csv( filename , index_col=0)
            
            df['year'], df['month'], df['day'] = self.date_to_year_month_day( df['Date'] )
            df['homeTeam'], df['awayTeam'], df['homeGoals'], df['awayGoals'] = self.result_to_columns( df['Result'])
            df['matchResults'] = df.apply( lambda x: self.add_match_results( x['homeGoals'], x['awayGoals'] ) ,axis=1 )
            
            self.df = df.drop( ['Date', 'Result'], axis = 1)
            self.df.to_csv( 'clean-' + filename , index=False)
            
        # return to parent directory
        os.chdir('..')
    
    
    def result_to_columns(self, lines):
        parsed = lines.apply( lambda res: self.parse_result_to_features( res) )
        result = np.vstack( np.array( parsed ) )
        return result[:,0], result[:,1], result[:,2], result[:,3]
    
    
    def parse_result_to_features(self, line ):
        words = line.split()
        n = len( words )
        goals = []
        for i in range( n ):
            if words[i].isdigit():
                goals.append(i)
                
        hometeam = ''.join( words[:goals[0]] )
        homeGoal = words[ goals[0] ]
        awayteam = ''.join(words[ goals[0] + 1: goals[1] ] )
        awayGoal = words[ goals[1] ]
        return hometeam, awayteam, homeGoal, awayGoal
    
    
    def date_to_year_month_day(self, dates):
        return dates.apply( lambda d: d // 10000 ) , dates.apply( lambda d: (d // 100) % 100), dates.apply( lambda d: d % 100 )
    
    
    def add_match_results(self, homegoals, awaygoals):
        result = 0
        if homegoals > awaygoals:
            result += 1
        elif homegoals < awaygoals:
            result -= 1
        return result
    

def main():
    filename = "predictz-20201025-to-20201027.csv"
    # set mode as append to add new data or else to clean
    mode = "normal"
    cleaner = Cleaner( filename , mode)
    
    cleanfilename = 'clean-'+filename
    # set mode as append to add new data or else to clean
    mode = "append"
    cleaner = Cleaner( cleanfilename , mode)
    
    
if __name__ == "__main__":
    main()
