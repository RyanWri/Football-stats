import pandas as pd
import os
import glob


class Model:
    def __init__(self):
        os.chdir('/Users/rywright/Football/Data')
        # find extension (csv in our case)
        extension = 'csv'
        all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
        # combine all files in the list
        combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])
        # export to csv
        combined_csv.to_csv("combined_csv.csv", index=False, encoding='utf-8-sig')


    @property
    def data(self):
        return self.df


def main():
    # to combine all data
    model = Model()


if __name__ == "__main__":
    main()