import pickle
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
from core.mutate import mutate_gene, mutate_gene_GCFSA
from core.config import multiprocessing_EA
import random
from multiprocessing import Pool
import os

core_count = os.cpu_count()

def create_offspring(args):
    p1, p2, data, mutation_rate, crossover_func, mutation_func, fitness_func = args
    c1, c2 = crossover_func(p1, p2)
    c1 = mutation_func(data, c1, mutation_rate)
    c2 = mutation_func(data, c2, mutation_rate)

    fit_c1 = fitness_func(c1, data)
    fit_p1 = fitness_func(p1, data)
    fit_c2 = fitness_func(c2, data)
    fit_p2 = fitness_func(p2, data)

    success_count = (fit_c1 < fit_p1) + (fit_c2 < fit_p2)
    return (c1, c2, success_count)


from core.config import tuning_dict
with open("data/heuristic_allocation.pkl", "rb") as f:
        data, encoded_df, section_map, subject_map, staff_map = pickle.load(f)

class EA:
    def __init__(self, population_size, max_generations, elitism_ratio, k=3, mutation_rate=0.3, replacement_ratio=0.0, crossover = "random", mr_tuning = False, mutation = "mutate_gene"):
        #print(mutation_rate, mr_tuning)
        self.population_size = population_size
        self.max_generations = max_generations
        self.elitism_size = int(elitism_ratio * population_size)
        self.k = k  
        self.mutation_rate = mutation_rate  
        self.population = [generate_gene(data, section_map) for _ in range(population_size)]
        self.best_solution = None
        self.best_fitness = float('inf')  
        self.best_list = []
        self.successful_mutations = [] 
        self.ema_successful_mutations = []  
        self.fitness_changes = []  
        self.ema_fitness_changes = []  
        self.generation = 0
        self.replacement_ratio = replacement_ratio
        self.mr_tuning = tuning_dict[mr_tuning] if mr_tuning != "None" else False
        if crossover == "random":
            self.crossover = crossover_random
        elif crossover == "biological":
            self.crossover = crossover_biological
        else:
            self.crossover = crossover_graph_based

        if mutation == "mutate_gene":
            self.mutation = mutate_gene
        else:
            self.mutation = mutate_gene_GCFSA
        

    def calc_fitness(self):
        self.population_fitness = [fitness(gene, data) for gene in self.population]

    def select_parents(self):
        self.parents = []
        for _ in range(self.population_size):
            batch = random.sample(range(self.population_size), self.k)
            chosen_one = min(batch, key=lambda idx: self.population_fitness[idx])
            self.parents.append(self.population[chosen_one])

    def next_gen(self):
        if self.mr_tuning:
            self.mutation_rate = self.mr_tuning[len(self.best_list)]
        #print(f"\nGeneration: {self.generation}, Mutation Rate: {self.mutation_rate}")
        self.calc_fitness()

        sorted_indices = sorted(range(self.population_size), key=lambda i: self.population_fitness[i])
        best_idx = sorted_indices[0]
        new_best_fitness = self.population_fitness[best_idx]

        fitness_change = - (new_best_fitness - self.best_fitness if self.best_fitness != float('inf') else 0)

        if new_best_fitness < self.best_fitness:
            self.best_fitness = new_best_fitness
            self.best_solution = self.population[best_idx]

        self.best_list.append(-self.best_fitness)
        self.fitness_changes.append(fitness_change)

        alpha = 0.5
        ema_value = alpha * fitness_change + (1 - alpha) * self.ema_fitness_changes[-1] if self.ema_fitness_changes else fitness_change
        self.ema_fitness_changes.append(ema_value)

        if self.best_fitness == 0:
            return True

        elites = [self.population[i] for i in sorted_indices[:self.elitism_size]]

        self.select_parents()
        next_gen = elites[:]

        successful = 0
        total_mutations = 0
        if multiprocessing_EA:
            pool = Pool(core_count)

            # Prepare input args list
            args_list = []
            needed = self.population_size // 2  # pairs per generation
            while len(next_gen) < self.population_size:
                p1, p2 = random.sample(self.parents, 2)
                args_list.append((p1, p2, data, self.mutation_rate, self.crossover, self.mutation, fitness))

                if len(args_list) == core_count or len(next_gen) + 2 * len(args_list) >= self.population_size:
                    results = pool.map(create_offspring, args_list)
                    args_list = []

                    for c1, c2, success_count in results:
                        next_gen.extend([c1, c2])
                        total_mutations += 2
                        successful += success_count
                        if len(next_gen) >= self.population_size:
                            break
            pool.close()
            pool.join()

        else:
            while len(next_gen) < self.population_size:
                p1, p2 = random.sample(self.parents, 2)
                c1, c2 = self.crossover(p1, p2)
                c1 = self.mutation(data, c1, self.mutation_rate)
                c2 = self.mutation(data, c2, self.mutation_rate)

                total_mutations += 2
                successful += (1 if fitness(c1, data) < fitness(p1, data) else 0)
                successful += (1 if fitness(c2, data) < fitness(p2, data) else 0)

                next_gen.extend([c1, c2])

        next_gen = next_gen[:self.population_size]

        random_count = max(1, int(self.replacement_ratio * self.population_size))
        random_individuals = [generate_gene(data, section_map) for _ in range(random_count)]

        next_gen[-random_count:] = random_individuals

        self.population = next_gen
        self.generation += 1

        success_ratio = successful / total_mutations if total_mutations > 0 else 0
        self.successful_mutations.append(success_ratio)

        ema_value = alpha * success_ratio + (1 - alpha) * self.ema_successful_mutations[-1] if self.ema_successful_mutations else success_ratio
        self.ema_successful_mutations.append(ema_value)

        return False


    def run(self):
        for _ in tqdm(range(self.generation, self.max_generations), desc="Evolving"):
            if self.next_gen():
                break
        return self.best_solution, self.best_fitness, self.best_list
