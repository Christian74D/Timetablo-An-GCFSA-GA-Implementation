import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm

def track_progress(future_to_run):
    total = len(future_to_run)
    completed = 0
    print(f"Total threads to be deployed: {total}")
    while completed < total:
        completed = sum(f.done() for f in future_to_run)
        print(f"Progress: {(completed / total) * 100:.2f}% - {completed}/{total} completed.", end='\r')
        time.sleep(.2)

def compute_average(fitness_sums, runs):
    return fitness_sums / runs

def plot_fitness(df, tuning_param):
    df_avg = df.groupby([tuning_param, "Generation"], as_index=False)["Fitness"].mean()
    tuning_values_sorted = sorted(df_avg[tuning_param].unique())
    colors = cm.viridis(np.linspace(0, 1, len(tuning_values_sorted)))

    plt.figure(figsize=(12, 6), dpi=300)
    for val, color in zip(tuning_values_sorted, colors):
        subset = df_avg[df_avg[tuning_param] == val]
        plt.plot(subset["Generation"], subset["Fitness"], label=f"{tuning_param}={val}", linewidth=2, color=color)

    plt.xlabel("Generation")
    plt.ylabel("Average Best Fitness")
    plt.title(f"Average Best Fitness Convergence for {tuning_param} Values")
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(True)
    plt.savefig(fr"outputs/{tuning_param}/comparison.png", dpi=400)
    print(f"Fitness plotted and saved to outputs/{tuning_param}/comparison.png")


def save_summary(df, time_records, tuning_param):
    # Convert time records to DataFrame
    df_time = pd.DataFrame(time_records, columns=["Run", tuning_param, "Time (s)"])

    # Get data for the last generation
    last_gen_num = df["Generation"].max()
    last_gen = df[df["Generation"] == last_gen_num]

    summary_rows = []
    for param_value, group in df.groupby(tuning_param):
        runs = group["Run"].unique()
        run_count = len(runs)

        # Time info for this param value
        param_time_df = df_time[df_time[tuning_param] == param_value].set_index("Run")["Time (s)"]
        gen_count = group["Generation"].max() + 1
        time_per_gen = param_time_df.mean() / gen_count  # assume uniform

        first_gen_neg5, first_gen_neg1 = None, None
        time_to_neg5, time_to_neg1 = None, None
        zero_fitness_runs = 0

        avg_fitness_by_gen = group.groupby("Generation")["Fitness"].mean()

        for gen, fitness in avg_fitness_by_gen.items():
            if first_gen_neg5 is None and fitness >= -5:
                first_gen_neg5 = gen
                time_to_neg5 = round(time_per_gen * gen, 2)
            if first_gen_neg1 is None and fitness >= -1:
                first_gen_neg1 = gen
                time_to_neg1 = round(time_per_gen * gen, 2)

        # Get all data for the current tuning param value
        param_group = group[group[tuning_param] == param_value]

        # Identify runs where **any generation** had fitness 0
        runs_with_zero_fitness = param_group[param_group["Fitness"] == 0]["Run"].unique()
        zero_fitness_runs = len(runs_with_zero_fitness)
        percent_zero_fitness = round((zero_fitness_runs / run_count) * 100, 2)


        # Aggregate stats
        last = last_gen[last_gen[tuning_param] == param_value]
        avg_fit = last["Fitness"].mean()
        min_fit = last["Fitness"].min()
        max_fit = last["Fitness"].max()
        std_fit = last["Fitness"].std()

        times = param_time_df
        avg_time = times.mean()
        min_time = times.min()
        max_time = times.max()
        std_time = times.std()

        summary_rows.append({
            tuning_param: param_value,
            "avg_fitness": avg_fit,
            "min_fitness": min_fit,
            "max_fitness": max_fit,
            "std_fitness": std_fit,
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "std_time": std_time,
            "gen_to_-5": first_gen_neg5,
            "gen_to_-1": first_gen_neg1,
            "time_to_-5": time_to_neg5,
            "time_to_-1": time_to_neg1,
            "%_zero_fitness": percent_zero_fitness
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(fr"outputs/{tuning_param}/summary_stats.csv", index=False)
    print(f"Saved summary stats to outputs/{tuning_param}/summary_stats.csv")
