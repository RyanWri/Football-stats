import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed


def split_match_data(outcome_string):
    correct_length = 4
    items = None

    temp = ''.join(outcome_string.split())
    match = re.match(r"([a-z]+)([0-9]+)([a-z]+)([0-9]+)", temp, re.I)
    if match:
        if len(match.groups()) == correct_length:
            items = match.groups()

    return items


def concurrent_crawl(start, end):
    '''
    :param start: start date( must be in this format year-month-day)
    :param end: end date( must be in this format year-month-day)
    :return: numpy array of league|home-team|home-score|away-team|away-score
    '''

    dates = []
    url = 'https://www.predictz.com/results/'
    for date in pd.date_range(start=start, end=end):
        dates.append(date.strftime("%Y%m%d"))

    content = []
    with ThreadPoolExecutor(max_workers=None) as Executor:
        jobs = {Executor.submit(crawl_site, url, date) for date in dates}
        for job in as_completed(jobs):
            date, matches = job.result()
            content.append(parse_match_soup_data(date, matches))

    return np.array(content)


def crawl_site(url, date):
    headers = {'Accept': '*/*',
               'Accept-Language': 'en-US,en;q=0.8',
               'Cache-Control': 'max-age=0',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    try:
        url = url + date + '/'
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
    matches = bs(attrs={'class': 'pzcnth1'})
    return date , matches


def parse_match_soup_data(date, matches):
    correct_length = 4
    results = []
    league_pos, team_pos = 2,3

    for match in matches:
        item = match.findAll('td')
        if len(item) != correct_length:
            continue
        else:
            league = item[league_pos].text
            outcome = item[team_pos].text
            match_data = split_match_data(outcome)
            if match_data:
                stats = [date, league, match_data[0], match_data[1], match_data[2], match_data[3]]
                results.append(stats)

    return np.array(results)


def run_main():
    start_date = '20200601'
    end_date = '20200630'
    content = concurrent_crawl(start_date, end_date)
    columns = 'date|league|home-team|home-score|away-team|away-score'.split('|')

    pdList = [pd.DataFrame(array, columns=columns) for array in content]
    new_df = pd.concat(pdList)
    new_df.to_csv(f'predictz-{start_date}-to-{end_date}.csv', index=False)


def main():
    run_main()


if __name__ == '__main__':
    main()
