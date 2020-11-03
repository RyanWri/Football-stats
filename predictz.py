'''
    predictZ site allow us to seperate games according to leagues so that is an improvement
    collect all data from 2020 and build detaild stats league by league
'''

import numpy as np
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures


def convert_to_bs4_object(url):
    session = requests.Session()
    timeout = 60
    headers = { 'Accept':'*/*', 'Accept-Language':'en-US,en;q=0.8', 'Cache-Control':'max-age=0',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    try:
        req = session.get(url, headers=headers, timeout = timeout )

    except requests.exceptions.RequestException:
        return None, None
    else:
        bs = BeautifulSoup(req.text, features = "lxml")
        date = url.replace('https://www.predictz.com/results/', '')
        return bs, date


def retrieve_matches_from_bs_object( bs ):
    wrapper = bs.find("div", id = "wrapper")
    if wrapper:
        content = wrapper.find( "div", id = "content")
        if content:
            contentfull = content.findAll( "div", class_= "contentfull" )
            if len(contentfull) >= 2: 
                widetable = contentfull[1].find("div", class_="widetable pb30")
                if widetable:
                    table = widetable.find("table", class_ = "pztable w100p")
                    if table:
                        matches = table.findAll("tr", class_ = "pzcnth1")
                        return matches
    
    return None


def retrieve_table_of_matches( soupObjects ):
    leagues = []
    outcomes = []
    dates = []
    for bs, date in soupObjects:
        matches = retrieve_matches_from_bs_object( bs )
        if matches:
            for match in matches:
                tds = match.findAll("td")
                if len(tds) == 4:
                    dates.append(date)
                    leagues.append( tds[2].text )
                    outcomes.append( tds[3].text )
            
    a = np.array( dates )
    b = np.array(leagues)
    c = np.array(outcomes)
    data = [a, b, c]
    return np.column_stack( data )
        

def concurrent_crawl(URLS):
    soupObjects = []
    dates = []
    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers = None) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(convert_to_bs4_object, url): url for url in URLS}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                bs, date = future.result()
                if bs and date:
                    soupObjects.append( (bs, date) )
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
    
    return soupObjects


def collect_fixtures_today():
    url = 'https://www.predictz.com/predictions/'
    session = requests.Session()
    timeout = 60
    headers = { 'Accept':'*/*', 'Accept-Language':'en-US,en;q=0.8', 'Cache-Control':'max-age=0',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    try:
        req = session.get(url, headers=headers, timeout = timeout )

    except requests.exceptions.RequestException:
        return [], []
    else:
        bs = BeautifulSoup(req.text, features = "lxml")
        hometeams, awayteams = [], []
        wrapper = bs.find("div", id = "wrapper")
        if wrapper:
            content = wrapper.find( "div", id = "content")
            if content:
                contentfull = content.findAll( "div", class_= "contentfull" )
                if len(contentfull) >= 3:
                    widetable = contentfull[2].find("div", class_="pttable mb30")
                    if widetable:
                        fixtures = widetable.findAll("div", class_ = "pttr ptcnt")
                        for game in fixtures:
                            home = game.find("div", class_ = "pttd ptmobh")
                            away = game.find("div", class_= "pttd ptmoba")
                            if home and away:
                                hometeams.append( home.text )
                                awayteams.append( away.text )
    
    return hometeams, awayteams
    

def  main():
    ###### To collect data set start and and date and remove the comment ########
    URLS = []
    dates = pd.date_range(start='2020-10-25', end='2020-10-27')
    for date in dates:
        URLS.append( 'https://www.predictz.com/results/' + date.strftime("%Y%m%d") )
    
    '''
    soupObjects = concurrent_crawl( URLS )
    data = retrieve_table_of_matches( soupObjects )
    df = pd.DataFrame( data, columns=["Date", "League", "Result"])    
    df.to_csv('predictz-20201025-to-20201027.csv')
    '''
    
    h, a = collect_fixtures_today()
    np.save( 'predictz-home', np.array(h) )
    np.save( 'predictz-away', np.array(a) )
    


if __name__ == "__main__":
    main()