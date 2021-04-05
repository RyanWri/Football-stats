from View.TeamStats import TeamStats
import os
import pandas as pd
import numpy as np


class Model:
    def __init__(self):
        self.team_stats = TeamStats()

    def calculate_draw_fixture(self,home_team, away_team):
        return self.team_stats.calculate_draw_fixture(home_team, away_team)

    def loc_team_raw_data(self, team_name):
        return self.team_stats.loc_team_raw_data(team_name)


def main():
    model = Model()
    h, a = model.calculate_draw_fixture('Lens', 'Paris St-G.')
    print(h)
    print(a)


if __name__ == "__main__":
    main()