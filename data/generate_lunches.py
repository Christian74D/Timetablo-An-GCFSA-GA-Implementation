import sys
import os
import pandas as pd
import random
from math import ceil
from collections import defaultdict

from core.constants import lunch_hours, days

def load_sections(file_path):
    section_df = pd.read_excel(file_path)
    return section_df['section'].tolist()

def load_data(file_path):
    df = pd.read_excel(file_path)
    return df.drop(columns=['id'], errors='ignore')

def allocate_lunches(sections, days, lunch_hours):
    num_sections = len(sections)
    num_hours = len(lunch_hours)
    ideal_per_hour = ceil(num_sections / num_hours)

    lunch_allocations = {section: [None] * days for section in sections}
    section_hour_counts = {section: defaultdict(int) for section in sections}

    for day in range(days):
        day_hour_counts = defaultdict(int)  # Tracks how many sections got each lunch hour today
        available_sections = sections[:]
        random.shuffle(available_sections)

        for section in available_sections:
            shuffled_hours = lunch_hours[:]
            random.shuffle(shuffled_hours)

            assigned = False
            for hour in shuffled_hours:
                if (section_hour_counts[section][hour] < ceil(days / num_hours) and
                        day_hour_counts[hour] < ideal_per_hour):
                    lunch_allocations[section][day] = hour
                    section_hour_counts[section][hour] += 1
                    day_hour_counts[hour] += 1
                    assigned = True
                    break

            if not assigned:
                # Fallback: assign the least used hour
                hour = min(lunch_hours, key=lambda h: day_hour_counts[h])
                lunch_allocations[section][day] = hour
                section_hour_counts[section][hour] += 1
                day_hour_counts[hour] += 1

    return lunch_allocations


def create_lunch_rows(lunch_allocations, sections, days, lunch_hours):
    lunch_rows = []
    for day in range(days):
        for hour in lunch_hours:
            secs = [s for s in sections if lunch_allocations[s][day] == hour]
            if secs:
                lunch_rows.append({
                    'sections': ', '.join(secs),
                    'subjects': f'LUNCH_DAY_{day+1}_HOUR_{hour}',
                    'staffs': '',
                    'theory': '',
                    'lab': '',
                    'block': f'({day+1},{hour})'
                })
    return lunch_rows

def save_combined_data(original_df, lunch_rows, file_path):
    combined_df = pd.concat([original_df, pd.DataFrame(lunch_rows)], ignore_index=True)
    combined_df.insert(0, 'id', range(1, len(combined_df) + 1))
    combined_df.to_excel(file_path, index=False)

def generate_lunches(src_path, section_path,  dest_path):
    sections = load_sections(section_path)
    df = load_data(src_path)
    lunch_allocations = allocate_lunches(sections, days, lunch_hours)
    lunch_rows = create_lunch_rows(lunch_allocations, sections, days, lunch_hours)
    save_combined_data(df, lunch_rows, dest_path)
    #print(f"Generated lunch data and saved to {dest_path}")

