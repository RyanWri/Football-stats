import pandas as pd
import os
import time
from datetime import date, timedelta

class SoccerBaseCleaner:
    def __init__(self, filename):
        os.chdir('/Users/rywright/Football/Data')

        df = pd.read_csv( filename )
        df['year'], df['month'], df['day'] = self.date_to_year_month_day( df['date'] )
        df['matchResults'] = df.apply( lambda x: self.add_match_results( x['homeGoals'], x['awayGoals'] ) ,axis=1 )
        self.df = df.drop( ['date'], axis = 1)
        self.df.to_csv( 'clean-' + filename , index=False)

        oldDatafilename = 'clean-soccerbase-total-data.csv'
        cleanfilename = 'clean-' + filename

        df = pd.read_csv(cleanfilename, index_col=0)
        # append clean data to complete csv
        df.to_csv(oldDatafilename, mode='a', header=False)


    def date_to_year_month_day(self, dates):
        fulldates = dates.apply( lambda d: time.strptime(d[3:], "%d%b %Y") )
        years = [d.tm_year for d in fulldates]
        months = [d.tm_mon for d in fulldates]
        days = [d.tm_mday for d in fulldates]
        return  years, months, days
    
    
    def add_match_results(self, homegoals, awaygoals):
        result = 0
        if homegoals > awaygoals:
            result += 1
        elif homegoals < awaygoals:
            result -= 1
        return result
    

def main():
    today = date.today()
    yesterday = today - timedelta(days=1)

    filename = f'data-from-{yesterday}-to-{yesterday}.csv'
    cleaner = SoccerBaseCleaner( filename )
    
    
if __name__ == "__main__":
    main()
