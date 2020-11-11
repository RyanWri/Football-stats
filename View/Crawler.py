import numpy as np
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import pandas as pd
import os
import concurrent.futures
from datetime import date, timedelta


class Crawler:
    def __init__(self, start , end):
        # date must be in this format year-day-month
        URLS = []
        dates = pd.date_range(start=start, end=end)
        for date in dates:
            URLS.append( 'https://www.soccerbase.com/matches/results.sd?date=' + date.strftime("%Y-%m-%d") )
        self.urls = np.array( URLS )
             
        
    def convert_to_bs4_object(self, url):
        session = requests.Session()
        timeout = 60
        headers = { 'Accept':'*/*',
                    'Accept-Language':'en-US,en;q=0.8',
                    'Cache-Control':'max-age=0',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
        try:
            req = session.get(url, headers=headers, timeout = timeout )
        except requests.exceptions.RequestException:
            return None
        bs = BeautifulSoup(req.text, features = "lxml")
        return bs
    
        
    def create_soup_object( self, soup):
        results = None
        body = siteContent = cpm = table = tbody = matchsoup = None
        
        if soup:
            body = soup.find("div", class_="body")
            if body:
                siteContent = body.find("div", class_="siteContent")
                if siteContent:
                    cpm = siteContent.find("div", id="cpm")
                    if cpm:
                        table = cpm.find("table", class_="soccerGrid listWithCards")
                        if table:
                            tbody = table.find("tbody")
                            if tbody:
                                matchsoup = tbody.findAll( "tr", class_= "match" )
            
        if body and siteContent and cpm and table and tbody and matchsoup:
            results = matchsoup
        
        return results
        
    
    def create_csv( self, matchsoup):
        columns = ['date', 'homeTeam', 'awayTeam', 'homeGoals', 'awayGoals']
        if not matchsoup:
            return pd.DataFrame(columns=columns)
        
        data =  []
        for match in matchsoup:
            homeTeam = match.find('td', class_= "team homeTeam").text
            awayTeam = match.find('td', class_= "team awayTeam").text
            score = match.find('td', class_= "score").find('a', class_="vs")
            if score:
                finalscore = score.findAll('em') 
                hoemGoals = finalscore[0].text
                awayGoals = finalscore[1].text
            else: # no score collected
                hoemGoals = -1
                awayGoals = -1
            date = match.find('td', class_="dateTime").find('span').find('a').text
            
            data.append( [date, homeTeam, awayTeam, hoemGoals, awayGoals] )
            
        
        df = pd.DataFrame( data, columns = columns )
        return df
    
    
    def concurrent_crawl(self):
        list_of_dataframes = []
        # We can use a with statement to ensure threads are cleaned up promptly
        with concurrent.futures.ThreadPoolExecutor(max_workers = None) as executor:
            # Start the load operations and mark each future with its URL
            future_to_url = {executor.submit(self.convert_to_bs4_object, url): url for url in self.urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    soup = future.result()
                    matchsoup = self.create_soup_object( soup )
                    df = self.create_csv( matchsoup )
                    list_of_dataframes.append( df )
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))
        
        finaldf = pd.concat(list_of_dataframes)           
        return finaldf
    
    
    def write_csv_to_file(self, df, filename ):
        os.chdir('../Data')
        df.to_csv( filename, index=False )
        os.chdir('..')
        
        
    def today_fixtures(self):
        teams = []
        
        url = 'https://www.soccerbase.com/matches/results.sd?date=' + date.today().strftime("%Y-%m-%d")
        soup = self.convert_to_bs4_object(url)
        if soup:
            matchsoup = self.create_soup_object(soup)
            if matchsoup:
                for match in matchsoup:
                    teams.append( match.find('td', class_= "team homeTeam").text )
                    teams.append( match.find('td', class_= "team awayTeam").text )

        os.chdir('/Users/rywright/Football/Data')
        np.save('soccer-base-teams', np.array(teams) )

                    
def main():
    # to run main just set start and end date and filename -> the results are in Data folder
    today = date.today()
    yesterday = today - timedelta(days=1)

    start = yesterday
    end = yesterday
    c = Crawler( start, end )

    # write today fixtures to np file
    c.today_fixtures()

    df = c.concurrent_crawl()
    filename = f'data-from-{start}-to-{end}.csv'
    c.write_csv_to_file( df,  filename)


if __name__ == "__main__":
    main()