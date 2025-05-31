from data.theory_lab_splitter import theory_lab_split
from data.generate_lunches import generate_lunches
from data.lab_allocator import lab_allocator
from data.data_formatter import format_timetable_data
from data.enocode_data import encoded_data
from core.config import input_path
import pandas as pd

def process_data(seed=""):
    base = "data/content/"
    
    theory_lab_split(input_path, f'{base}split_data{seed}.xlsx')
    
    encoded_data(
        input_path,
        f'{base}encoded_data{seed}.xlsx',
        f'{base}section_codes{seed}.xlsx',
        f'{base}staff_codes{seed}.xlsx',
        f'{base}subject_codes{seed}.xlsx'
    )
    
    generate_lunches(
        f'{base}split_data{seed}.xlsx',
        f'{base}section_codes{seed}.xlsx',
        f'{base}data_with_lunch{seed}.xlsx'
    )
    
    format_timetable_data(
        f'{base}data_with_lunch{seed}.xlsx',
        f'{base}timetable_data_without_labs{seed}.pkl'
    )
    
    data = lab_allocator(
        f'{base}timetable_data_without_labs{seed}.pkl',
        f'{base}section_codes{seed}.xlsx',
        f"{base}data_lunch_lab_allocated{seed}.xlsx"
    )
    
    encoded_df, section_map, subject_map, staff_map = encoded_data(
        f'{base}data_lunch_lab_allocated{seed}.xlsx',
        f'{base}encoded_data{seed}.xlsx',
        f'{base}section_codes{seed}.xlsx',
        f'{base}staff_codes{seed}.xlsx',
        f'{base}subject_codes{seed}.xlsx'
    )
    
    return data, encoded_df, section_map, subject_map, staff_map
