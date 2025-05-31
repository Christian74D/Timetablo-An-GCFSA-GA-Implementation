import pandas as pd
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

from core.config import *
from core.run_ea import run_ea
from core.utils import track_progress, compute_average, plot_fitness, save_summary
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
with open("data/heuristic_allocation.pkl", "rb") as f:
        data, encoded_df, section_data, subject_map, staff_map = pickle.load(f)


results = []
time_records = []
fixed_params.pop(tuning_param, None)

def main():
    #gene = generate_gene(data, section_data)
    #print("Initial Gene:", gene)
    #print(fitness(gene, data))
    #plot_timetables_for_all_sections(gene, "sample.pdf")
    #return None
    if use_multithreading_main:
        with ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(run_ea, fixed_params, tuning_param, tuning_value, run_idx, max_generations, runs_per_setting): (tuning_value, run_idx)
                for tuning_value in tuning_values
                for run_idx in range(runs_per_setting)
            }
            track_progress(futures)

            for future in as_completed(futures):
                raw_data, fitness_sums, elapsed = future.result()
                #print(raw_data)
                tuning_value, run_idx = futures[future]
                results.extend(raw_data)
                time_records.append([run_idx, tuning_value, elapsed])
                #avg_fitness = compute_average(fitness_sums, runs_per_setting)
                #print("avg", avg_fitness)
                #for gen, avg_fit in enumerate(avg_fitness):
                #    results.append([run_idx, tuning_value, gen, avg_fit, elapsed])
                #print("Results:", results)
    else:
        for tuning_value in tqdm(tuning_values, desc="Tuning Progress"):
            for run_idx in tqdm(range(runs_per_setting), leave=False):
                raw_data, fitness_sums, elapsed = run_ea(fixed_params, tuning_param, tuning_value, run_idx, max_generations, runs_per_setting)
                results.extend(raw_data)
                time_records.append([run_idx, tuning_value, elapsed])
                #avg_fitness = compute_average(fitness_sums, runs_per_setting)
                #for gen, avg_fit in enumerate(avg_fitness):
                #    results.append([run_idx, tuning_value, gen, avg_fit, elapsed])

    df = pd.DataFrame(results, columns=["Run", tuning_param, "Generation", "Fitness", "Time (s)"])
    df.to_csv(f"outputs/{tuning_param}/fitness_results.csv", index=False)
    print(f"Saved all results to outputs/{tuning_param}/fitness_results.csv")
    plot_fitness(df, tuning_param)
    save_summary(df, time_records, tuning_param)

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    time_str = calculate_time(start, end)
    print(time_str)
    save_time_to_file(time_str)