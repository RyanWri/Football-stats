import pandas as pd
import os
import time


class SoccerBaseCleaner:
    def __init__(self, filename):
        os.chdir('/Users/rywright/Football/Data')

        df = pd.read_csv( filename )
        df['year'], df['month'], df['day'] = self.date_to_year_month_day( df['date'] )
        df['matchResults'] = df.apply( lambda x: self.add_match_results( x['homeGoals'], x['awayGoals'] ) ,axis=1 )

        data = df.drop( ['date'], axis = 1)
        self.df = self.clean_minus_1( data )


    def date_to_year_month_day(self, dates):
        fulldates = dates.apply( lambda d: time.strptime(d[3:], "%d%b %Y") )
        years = [d.tm_year for d in fulldates]
        months = [d.tm_mon for d in fulldates]
        days = [d.tm_mday for d in fulldates]
        return  years, months, days
    
    
    def add_match_results(self, homegoals, awaygoals):
        result = 'D'
        if homegoals > awaygoals:
            result = 'H'
        elif homegoals < awaygoals:
            result = 'A'
        return result


    def clean_minus_1(self, df):
        df['homeTeam'] = df['homeTeam'].apply(lambda team: team.replace('-1', ''))
        df['awayTeam'] = df['awayTeam'].apply(lambda team: team.replace('-1', ''))
        finaldf = df.loc[(df['homeGoals'] >= 0) & (df['awayGoals'] >= 0)].copy()
        return finaldf


    def write_clean_csv(self, filename):
        self.df.to_csv(filename, index=False)
        os.chdir('..')


def main():
    filename = f'data-from-2020-08-01-to-2020-12-13.csv'
    cleaner = SoccerBaseCleaner( filename )

    cleanfilename = 'clean' + filename
    cleaner.write_clean_csv( cleanfilename )
    
    
if __name__ == "__main__":
    main()
