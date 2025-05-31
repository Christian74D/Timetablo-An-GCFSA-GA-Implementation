import string
import random
import time
import pickle
from copy import deepcopy
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import networkx as nx
from tqdm import tqdm
import pickle

from core.time import calculate_time, save_time_to_file
from core.constants import data_path
from core.plot_student_timetable import plot_timetables_for_all_sections
from core.generate_individual import generate_gene
from core.mutate import mutate_gene
from core.fitness_calculator import fitness
from core.crossover_functions import crossover_random, crossover_biological, crossover_graph_based


import time
import numpy as np
from core.EA import EA 
from core.plot_student_timetable import plot_timetables_for_all_sections
from core.plot_staff_timetable import plot_timetables_for_all_staff

def run_ea(fixed_params, tuning_param, tuning_value, run_idx, max_generations, runs_per_setting):
    start_time = time.time()
    fitness_sums = np.zeros(max_generations)

    ea = EA(**fixed_params, **{tuning_param: tuning_value})
    sol, fitness, fitness_history = ea.run() 

    #timetable plotting
    filename = f"timetable_fitness_{int(fitness)}_{tuning_param}_{tuning_value}_run_{run_idx}.pdf"
    plot_timetables_for_all_sections(sol, filename)
    plot_timetables_for_all_staff(sol, filename)
    #print(fitness_history)
    fitness_sums[:len(fitness_history)] += fitness_history
    #print(fitness_sums)
    elapsed = time.time() - start_time

    return [
        (run_idx, tuning_value, gen, fitns, elapsed)
        for gen, fitns in enumerate(fitness_history)
    ], fitness_sums, elapsed


