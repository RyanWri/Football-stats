import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
import os


class Crawler:
    def __init__(self):
        # date must be in this format year-month-day
        self.url = "https://www.soccerbase.com/matches/results.sd?date="

    def get_matches_as_bs4_from_url(self, formatted_date):
        url = self.url + formatted_date
        timeout = 60
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.8",
            "Cache-Control": "max-age=0",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        try:
            r = requests.get(url, timeout=60, headers=headers)
        except requests.exceptions.RequestException as e:
            return e

        bs = BeautifulSoup(r.text, "html.parser")
        class_names = ["dateTime", "team homeTeam", "team awayTeam", "vs"]
        matches = self.find_class_in_bs4(bs, class_names)
        return matches

    @staticmethod
    def find_class_in_bs4(bs, class_names):
        result = dict()
        for name in class_names:
            stats = []
            for value in bs(attrs={"class": name}):
                stats.append(value.text)
            result[name] = stats
        return result

    def concurrent_crawl(self, start, end):
        dates = [
            formatted_date.strftime("%Y-%m-%d")
            for formatted_date in pd.date_range(start=start, end=end)
        ]
        stats = []
        # We can use a with statement to ensure threads are cleaned up promptly
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            # Start the load operations and mark each future with its URL
            matches_dict = {
                executor.submit(self.get_matches_as_bs4_from_url, d): d for d in dates
            }
            for future in concurrent.futures.as_completed(matches_dict):
                url = matches_dict[future]
                try:
                    result = self.dict_to_dataframe(future.result())
                    stats.append(result)
                except Exception as exc:
                    print("%r generated an exception: %s" % (url, exc))

        df = pd.concat(stats, ignore_index=True)
        self.clean_and_write_data(df, start, end)

    @staticmethod
    def dict_to_dataframe(stats_dict):
        result = []
        for a, b, c, d in zip(*stats_dict.values()):
            record = [a, b, c, d]
            result.append(record)

        stats = np.array(result)
        df = pd.DataFrame(stats, columns=["date", "home-team", "away-team", "score"])
        return df

    @staticmethod
    def clean_and_write_data(df, start, end):
        data = df[df["score"] != "v"].copy()
        data["home-goals"] = data.score.apply(lambda x: x.split("-")[0]).astype(int)
        data["away-goals"] = data.score.apply(lambda x: x.split("-")[1]).astype(int)
        dates = []
        for d in data["date"]:
            formatted_date = "".join(d.split()[1:])
            dates.append(pd.to_datetime(formatted_date, format="%d%b%Y"))
        data["formatted-date"] = dates
        data["home-won"] = np.where(data["home-goals"] > data["away-goals"], 1, 0)
        data["away-won"] = np.where(data["home-goals"] < data["away-goals"], 1, 0)
        data["draw"] = np.where(data["home-goals"] == data["away-goals"], 1, 0)
        clean_data = data.drop(["date", "score"], axis=1)
        os.chdir("/Users/rywright/Football/CsvData")
        clean_data.to_csv(f"SoccerBase-{start}-{end}.csv", index=False)


def main():
    # to run main just set start and end date and filename -> the results are in CsvData folder
    start = "2021-05-11"
    end = "2021-06-14"
    c = Crawler()
    c.concurrent_crawl(start, end)


if __name__ == "__main__":
    main()
