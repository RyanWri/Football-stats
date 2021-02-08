import pandas as pd
import os
import numpy as np
import glob


def add_match_results(home, away):
    outcomes = []
    for h,a in zip(home, away):
        outcome = '1' if h > a else '2' if a > h else 'X'
        outcomes.append(outcome)

    return np.array(outcomes)


def predictz_combiner():
    os.chdir('/Users/rywright/Football/CSVData')

    # read and concat all csv
    all_filenames = [i for i in glob.glob('*.csv')]
    combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])

    # add outcomes and set date as index
    combined_csv['matchResults'] = add_match_results(combined_csv["home-score"], combined_csv["away-score"])
    combined_csv['date'] = pd.to_datetime(combined_csv['date'], format='%Y%m%d')
    data = combined_csv.set_index('date').sort_index(ascending=False)

    # write final data into new csv
    os.chdir('/Users/rywright/Football/Data')
    data.to_csv(f'predictz-july2020-to-january2021.csv', encoding='utf-8-sig')


def main():
    predictz_combiner()


if __name__ == "__main__":
    main()
