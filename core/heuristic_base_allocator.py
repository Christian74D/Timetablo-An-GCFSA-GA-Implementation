from data.data_processor import process_data
from core.generate_individual import generate_gene
from core.constants import ImpossibleAllocationError, allocation_attempts, heuristic_trials, heuristic_samples
from core.config import use_multithreading_setup
from copy import deepcopy
import pickle
import random
from tqdm import tqdm
from datetime import datetime

import random
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


def score(seed):
    random.seed(seed)
    data, encoded_df, section_map, subject_map, staff_map = process_data(seed)
    score = 0
    for _ in range(heuristic_trials):
        data_copy = deepcopy(data)  
        try:              
            h = generate_gene(data_copy, section_map, heuristic=True)
            score += h
        except ImpossibleAllocationError:
            score += allocation_attempts + 1 #if allocation fails, add a large number to the score
    #print(f"Seed: {seed}, Score: {score}")
    return score

def generate_heuristic_allocation():
    def evaluate_seed(seed):
        random.seed(seed)
        return seed, score(seed)

    min_score = float('inf')
    best_seed = 0

    if use_multithreading_setup:
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(evaluate_seed, seed): seed for seed in range(heuristic_samples)}
            for future in tqdm(as_completed(futures), total=heuristic_samples, desc="Finding best seed"):
                seed, sscore = future.result()
                if sscore < min_score:
                    best_seed = seed
                    min_score = sscore
    else:
        scores = []
        for seed in tqdm(range(heuristic_samples), desc="Finding best seed"):
            random.seed(seed)
            sscore = score(seed)
            scores.append(sscore)
            if sscore < min_score:
                best_seed = seed
                min_score = sscore


    print(f"Best seed: {best_seed} with score: {score(best_seed)}")
    print("Heuristic Base Allocation Completed")

    random.seed(best_seed)
    with open("seeds.txt", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} - Seed used: {best_seed} - Score List - {scores}\n")

    return process_data()


if __name__ == "__main__":
    with open("data/heuristic_allocation.pkl", "wb") as f:
        pickle.dump(generate_heuristic_allocation(), f)