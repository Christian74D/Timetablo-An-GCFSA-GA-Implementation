import numpy as np
import os

actual_data = 'data/data.xlsx'
sim_data = 'simulations/synthetic_data_10.xlsx'
input_path = actual_data
use_multithreading_setup = False
use_multithreading_main = True
multiprocessing_EA = False
max_generations = 5
runs_per_setting = 1
mr = 0.01

tuning_param = "mutation"
tuning_values = ["mutate_gene_GCFSA"]*6  # "mutate_gene", "mutate_gene_GCFSA"



output_dir = f"outputs/{tuning_param}"
os.makedirs(output_dir, exist_ok=True)

#tuning_param = "mr_tuning"#"mutation_rate""crossover"
#tuning_values = ["const", "cyclic","cyclic2"]#[0.001, 0.01, 0.02, 0.03, 0.06]["random", "graph_based", "biological"]

def cyclic_decay_schedule(base_mr, delta, cycle_len, step, max_generations):
    schedule = []
    current_len = cycle_len
    while len(schedule) < max_generations and current_len >= 1:
        values = np.linspace( base_mr + delta, base_mr - delta,current_len).tolist()
        schedule.extend(values)
        current_len = max(1, current_len - step)
    
    return schedule[:max_generations]

#mr tuning
tuning_dict = {
    "const": [mr] * max_generations,
    "cyclic":  cyclic_decay_schedule(base_mr=0.03, delta=0.005, cycle_len=5, step=0, max_generations=max_generations),
    "cyclic2": cyclic_decay_schedule(base_mr=0.03, delta=0.01, cycle_len=7, step=2, max_generations=max_generations),
}

fixed_params = {
    "max_generations": max_generations,
    "mutation": "mutate_gene",
    "population_size": 100,
    "mutation_rate": mr,
    "k": 3,
    "elitism_ratio": 0.05,
    "crossover": "random",
    "replacement_ratio": 0.05,
    "mr_tuning": "None"
}
