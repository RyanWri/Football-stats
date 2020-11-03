import pandas as pd
import numpy as np
import os
from datetime import date
import sys
import math
import pickle


class Draw:
    def __init__(self, dataFilenmae, mode='predictz'):
        os.chdir('Data')
        df = pd.read_csv( dataFilenmae )
        self.data = df.sort_values(['year', 'month', 'day'], ascending=[False, False, False])
        
        teamsfilename = 'predictz-teams.pkl' if mode == 'predictz' else 'soccerbase-teams.pkl'
        pkl_file = open( teamsfilename, 'rb')
        self.teamsDrawStats = pickle.load(pkl_file)
        pkl_file.close()
        os.chdir('..')
            
            
    def calc_probability_per_match(self, hometeam, awayteam):
        homeprob = self.is_worth_looking( hometeam )
        awayprob = self.is_worth_looking( awayteam )
        return (homeprob, awayprob)
        
    
    def is_worth_looking(self, team):
        if team in self.teamsDrawStats.keys():
            record = self.teamsDrawStats[ team ]
            # record looks like this [ frequency, mean-cycles, max in cycles, current streak]
            freq = True if record[0] > 0.0 and record[0] <= 3.0 else False 
            mean = True if record[1] > 0.0 and record[1] <= 4.0 else False
            maxdraw = True if record[2] > 0.0 and record[2] <= 8.0 else False 
            streak = True if record[3] <= record[2] else False
            result = freq and mean and maxdraw and streak
            return result
            
        else:
            return False
    
    
    def delete_spaces(self, arr):
        result = []
        for a in arr:
            val = a.split()
            if len( val ) > 1:
                result.append( ''.join( val ) )
            else:
                result.append( a )
                
        return result
    
        
    def get_fixtures(self, mode):
        os.chdir("Data")
        
        if mode == 'predictz':
            home = np.load("predictz-home.npy")
            h = self.delete_spaces(home)
            away = np.load("predictz-away.npy")
            a = self.delete_spaces(away)
        else:
            h = np.load('soccer-base-home.npy')
            a = np.load('soccer-base-away.npy')    
            
        os.chdir("..")
        return h, a
    
    
    def write_probabilites_to_csv( self, mode):
        hteams, ateams = self.get_fixtures( mode )
        
        probs = np.array( [self.calc_probability_per_match(h,a) for h,a in zip(hteams, ateams) ])
        homeprob, awayprob= probs[:,0], probs[:,1]
        results = np.column_stack( [hteams, ateams, homeprob, awayprob] )
          
        cols = ['homeTeam', 'awayTeam', 'homeWorthLooking', 'awayWorthLooking']
        df = pd.DataFrame(results, columns=cols)
        
        filename = 'probabilities-predictz.csv' if mode == 'predictz' else 'probabilities-soccerbase.csv'
        df.to_csv( filename )

    
def main():
    # soccer base stats
    soccerFilenmae = 'clean-soccerbase-total-data.csv'    
    mode = 'soccerbase'
    soccerbase = Draw( soccerFilenmae )
    soccerbase.write_probabilites_to_csv( mode )
    
    
    # predictz stats
    predictzFilename = 'clean-total-data.csv'
    mode = 'predictz'
    predictz = Draw( predictzFilename )
    predictz.write_probabilites_to_csv( mode )
    
    
if __name__ == "__main__":
    main()