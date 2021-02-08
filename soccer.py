import numpy as np
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import glob


def crawl_site(url):
    headers = {'Accept': '*/*',
               'Accept-Language': 'en-US,en;q=0.8',
               'Cache-Control': 'max-age=0',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    try:
        r = requests.get(url, timeout=60, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)

    bs = BeautifulSoup(r.text, features="lxml")
    matches = bs(attrs={'class': 'match'})
    date = url.replace('https://www.soccerbase.com/matches/results.sd?date=','')
    return date , matches


def build_dataframe_from_matches(date, matchsoup):
    '''
    :param date: date of given matches
    :param matchsoup: list of all matches as beautifoul soup object
    :return: dataframe of parsed matches
    '''
    columns = ['date', 'homeTeam', 'awayTeam', 'homeGoals', 'awayGoals']

    data = []
    for match in matchsoup:
        homeTeam = match.find('td', class_="team homeTeam").text
        awayTeam = match.find('td', class_="team awayTeam").text
        score = match.find('td', class_="score").find('a', class_="vs")
        if score:
            finalscore = score.findAll('em')
            hoemGoals = finalscore[0].text
            awayGoals = finalscore[1].text
        else:  # no score collected
            hoemGoals = -1
            awayGoals = -1
        data.append([date, homeTeam, awayTeam, hoemGoals, awayGoals])

    df = pd.DataFrame(data, columns=columns)
    return df


def concurrent_crawl(start, end):
    '''

    :param start: start date and end date ( must be in this format year-month-day)
    :param end: array of html items
    :return: soccerbase date for given dates
    '''

    urls = []
    for date in pd.date_range(start=start, end=end):
        urls.append('https://www.soccerbase.com/matches/results.sd?date=' + date.strftime("%Y-%m-%d"))

    content = []
    with ThreadPoolExecutor(max_workers=None) as Executor:
        jobs = {Executor.submit(crawl_site, url) for url in urls}
        for job in as_completed(jobs):
            date, matches = job.result()
            df = build_dataframe_from_matches(date, matches)
            content.append(df)

    return content


def add_match_results(homegoals, awaygoals):
    result = 'D'
    if homegoals > awaygoals:
        result = 'H'
    elif homegoals < awaygoals:
        result = 'A'
    return result


def clean_matches_before_writing(content):
    '''
    :param content: list of dataframes
    :return: clean data with valid scores
    '''
    df = pd.concat(content)
    df['homeGoals'] = df['homeGoals'].astype('int')
    df['awayGoals'] = df['awayGoals'].astype('int')
    df = df[(df['homeGoals'] >= 0) & (df['awayGoals'] >= 0)]
    df['matchResults'] = df.apply(lambda x: add_match_results(x['homeGoals'], x['awayGoals']), axis=1)
    return df


def crawl_matches_to_csv():
    '''
    :param start: format %Year-%month-%day from user
    :param end: must be later than start
    :param filename: filename clean-matches-from-start-to-end.csv
    :return: no return , only writing file
    '''
    start = input("Enter start date %Year-%month-%day ")
    end = input("Enter end date in the format %Year-%month-%day")
    filename = f'clean-matches-from-{start}-to-{end}.csv'

    content = concurrent_crawl(start, end)
    df = clean_matches_before_writing(content)
    os.chdir('Data')
    df.to_csv(filename, index=False)
    os.chdir('..')


def read_dataframe(filename):
    os.chdir('Data')
    df = pd.read_csv('clean-matches-from-2020-06-01-to-2020-12-22.csv')
    os.chdir('..')
    return df


def saveTodayFixturesAsNumpyFile():
    fixtures = []
    url = 'https://www.soccerbase.com/matches/results.sd'
    date, matches = crawl_site(url)
    for match in matches:
        homeTeam = match.find('td', class_="team homeTeam").text
        awayTeam = match.find('td', class_="team awayTeam").text
        fixtures.append( [homeTeam, awayTeam])

    with open('fixtures.npy', 'wb') as f:
        np.save(f, fixtures)
    f.close()

    return np.array(fixtures)


def calculateStatsPerTeam(df, team):
    '''
    :param df: dataframe with matches stats for specific team
    :return: record with ppg, goals per game, lose win and draw rate.
    '''
    try:
        home = df[df['homeTeam'] == team]
        away = df[df['awayTeam'] == team]
        #points = [3 if x == 'H' else (1 if x == 'D' else 0) for x in home['matchResults']]
        #points += [3 if x == 'A' else (1 if x == 'D' else 0) for x in away['matchResults']]
        #ppg = np.sum(points) / len(points)

        homegames = ''.join(home['matchResults'].values)
        awaygames = ''.join(away['matchResults'].values)
        total = len(homegames) + len(awaygames)

        win = (homegames.count('H') + awaygames.count('A'))/ total
        draw = (homegames.count('D') + awaygames.count('D'))/ total
        lose = (homegames.count('A') + awaygames.count('H'))/ total

        goals_scored = (np.sum(home['homeGoals']) + np.sum(away['awayGoals'])) / (len(home['homeGoals']) + len(away['awayGoals']))
        goals_conceived = (np.sum(home['awayGoals']) + np.sum(away['homeGoals'])) / (len(home['awayGoals']) + len(away['homeGoals']))
        stats = {'ppg':0, 'win':win, 'draw':draw, 'lose':lose, 'scored':goals_scored, 'conceived':goals_conceived}
    except ZeroDivisionError:
        stats = None
    else:
        return stats


def calculateStreakPerTeam(df, team):
    outcomes = df[(df['homeTeam'] == team) | (df['awayTeam'] == team)]
    descending = outcomes.sort_values(by='date', ascending=False)['matchResults'].values
    streak = ''.join(descending).split('D')
    return len(streak[0])


def build_today_fixtures_csv():
    '''
    :return: csv with today teams stats
    '''
    filename = 'clean-total-matches.csv'
    df = read_dataframe(filename)
    with open('fixtures.npy', 'rb') as f:
        fixtures = np.load(f)

    columns = 'win|draw|lose|home-ppg|away-ppg|scored|conceived'
    stats, records = dict(), dict()
    for match in fixtures:
        h, a = match[0], match[1]
        stats[h], stats[a] = calculateStatsPerTeam(df,h), calculateStatsPerTeam(df,a)
        if not stats[h] or not stats[a]:
            break
        else:
            win, draw, lose = stats[h]['win'] * stats[a]['lose'], stats[h]['draw'] * stats[a]['draw'], stats[h]['lose'] * stats[a]['win']
            total = win + draw + lose
            tmp = {'win': win / total, 'draw': draw / total, 'lose': lose / total, 'homePPG': stats[h]['ppg'],
                   'awayPPG': stats[a]['ppg'], 'scored': stats[h]['scored'] - stats[a]['conceived'],
                    'conceived': stats[a]['scored'] - stats[h]['conceived']}
            records[f'{h} vs {a}'] = tmp

    todayDf = pd.DataFrame.from_dict(records,orient='index',columns=columns.split('|'))
    todayDf.to_csv('today-fixtures-stats.csv')
    f.close()


def collect_all_csv_to_current_date():
    path = "/Users/rywright/Football/Data/*.csv"
    content = []
    for fname in glob.glob(path):
        content.append(pd.read_csv(fname))

    df = pd.concat(content)
    df.to_csv('clean-total-matches.csv')


def main():
    '''
    crawl_matches_to_csv()
    collect_all_csv_to_current_date()
    '''
    #saveTodayFixturesAsNumpyFile()
    #build_today_fixtures_csv()
    df = pd.read_csv('clean-total-matches.csv')
    team = 'Arsenal'
    print( calculateStreakPerTeam(df, team) )


if __name__ == '__main__':
    main()
