import pandas as pd
import os

def load_data(file_path):
    return pd.read_excel(file_path)

def generate_codes(df, column_name, prefix):
    items = []
    for _, row in df.iterrows():
        items.extend([s.strip() for s in str(row[column_name]).split(',')])
    sorted_items = sorted(set(items))
    generated_codes = [f"{prefix}_{str(i).zfill(3)}" for i in range(len(sorted_items))]
    return sorted_items, generated_codes

def save_to_excel(data, file_name, columns):
    df = pd.DataFrame(data, columns=columns)
    df.to_excel(file_name, index=False)

def section_sort_key(section):
    parts = section.split('_')
    try:
        sem = int(parts[0])
        sec = parts[-1]
    except (IndexError, ValueError):
        sem, sec = 0, ''
    return (sem, sec)

def merge_data(df, section_map, subject_map, staff_map):
    encoded_rows = []
    for _, row in df.iterrows():
        sections = [section_map.get(s.strip(), s.strip()) for s in str(row['sections']).split(',')]
        subjects = [subject_map.get(s.strip(), s.strip()) for s in str(row['subjects']).split(',')]
        staffs = [staff_map.get(s.strip(), s.strip()) for s in str(row['staffs']).split(',')]
        encoded_row = row.copy()
        encoded_row['sections'] = ', '.join(sections)
        encoded_row['subjects'] = ', '.join(subjects)
        encoded_row['staffs'] = ', '.join(staffs)
        encoded_rows.append(encoded_row)
    return pd.DataFrame(encoded_rows)

def encoded_data(src_path, dest_path, section_path, staff_path, subject_path):
    df = load_data(src_path)

    subject_codes, generated_subject_codes = generate_codes(df, 'subjects', 'SUB')
    save_to_excel(list(zip(subject_codes, generated_subject_codes)), subject_path, ['subject_code', 'generated_code'])

    staff_names, generated_staff_codes = generate_codes(df, 'staffs', 'FAC')
    save_to_excel(list(zip(staff_names, generated_staff_codes)), staff_path, ['staff_name', 'generated_code'])

    sections, generated_section_codes = generate_codes(df, 'sections', 'SEC')
    sections = sorted(sections, key=section_sort_key)
    save_to_excel(list(zip(sections, generated_section_codes)), section_path, ['section', 'generated_code'])

    section_map = dict(zip(sections, generated_section_codes))
    subject_map = dict(zip(subject_codes, generated_subject_codes))
    staff_map = dict(zip(staff_names, generated_staff_codes))

    encoded_df = merge_data(df, section_map, subject_map, staff_map)
    encoded_df.to_excel(dest_path, index=False)

    #print(f"Encoded data saved to {dest_path}")
    #print(f"Section codes saved to {section_path}")
    #print(f"Staff codes saved to {staff_path}")
    #print(f"Subject codes saved to {subject_path}")

    return encoded_df, section_map, subject_map, staff_map
