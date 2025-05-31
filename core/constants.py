import pandas as pd
import pickle
import os
from reportlab.lib import colors

base_dir = os.path.dirname(__file__)
data_dir = os.path.join(base_dir, "..", "data")
DAYS = 5
HOURS = 8

allocation_attempts = 100
heuristic_trials = 20
heuristic_samples = 100

lunch_color = colors.green
multisec_color = colors.violet
blocked_color = colors.grey

data_path = 'data/timetable_data.pkl'

days = 5
lunch_hours = [4, 5]

allowed_lab_configs = {2: [(1, 2), (3, 4), (5, 6), (7, 8)],
                       3:[(1, 2, 3), (2, 3, 4), (5, 6, 7), (6, 7, 8)]}

class ImpossibleAllocationError(Exception):
    pass