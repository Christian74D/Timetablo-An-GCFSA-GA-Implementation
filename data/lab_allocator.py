import pickle
import random
import pandas as pd
from core.constants import DAYS, HOURS, allowed_lab_configs, data_path
from copy import deepcopy

def load_sections(file_path):
    section_df = pd.read_excel(file_path)
    return section_df['section'].tolist()

def allocate_labs(gene, data, section_data):
    #print(data)
    retries = 0
    while True:
        retries += 1
        success = True
        gene_copy = deepcopy(gene)

        free_slots = {
            sec: {(day, hour) for day in range(DAYS) for hour in range(HOURS)}
            for sec in section_data
        }

        # Precompute staff mapping
        staff_by_id = {item["id"]: item["staffs"] for item in data}
        all_staff_ids = {staff for staffs in staff_by_id.values() for staff in staffs}
        free_slots_faculty = {
            staff: {(day, hour) for day in range(DAYS) for hour in range(HOURS)}
            for staff in all_staff_ids
        }

        # Update free slots based on current gene
        for sec in section_data:
            for day in range(DAYS):
                for hour in range(HOURS):
                    cell = gene_copy[sec][day][hour]
                    if cell is not None:
                        free_slots[sec].discard((day, hour))
                        subject_id = cell[0]
                        for staff in staff_by_id[subject_id]:
                            free_slots_faculty[staff].discard((day, hour))

        for item in data:
            lab_len = item["lab"]
            if lab_len <= 0:
                continue

            configs = allowed_lab_configs.get(lab_len, [])
            if not configs:
                print(f"No allowed config for lab length {lab_len} in item {item['id']}")
                continue

            possible_blocks = [(day, [c - 1 for c in cfg]) for day in range(DAYS) for cfg in configs]
            random.shuffle(possible_blocks)

            item_success = False
            for day, cfg in possible_blocks:
                if all(all((day, hour) in free_slots[sec] for sec in item["sections"]) for hour in cfg) and \
                   all(all((day, hour) in free_slots_faculty[staff] for staff in item["staffs"]) for hour in cfg):

                    for sec in item["sections"]:
                        for hour in cfg:
                            gene_copy[sec][day][hour] = (item["id"], item["subjects"])
                            free_slots[sec] = {slot for slot in free_slots[sec] if slot[0] != day}

                    for staff in item["staffs"]:
                        free_slots_faculty[staff].discard((day, hour))


                    item["block"] = [(day, hour) for hour in cfg]
                    item_success = True
                    break

            if not item_success:
                success = False
                #print(f"Failed to allocate item {item['id']} {item['staffs']} {item['sections']} {item['lab']}")
                break  # retry whole allocation

        if success:
            #print(f"Lab allocation succeeded after {retries} attempt(s)")
            return gene_copy


def lab_allocator(input_path, section_path, op_path):
    section_data = load_sections(section_path)    
    with open(input_path, 'rb') as f:
        data = pickle.load(f)

    # Initialize gene structure
    gene = {
        sec: [[None for _ in range(HOURS)] for _ in range(DAYS)]
        for sec in section_data
    }

    # Fill gene with pre-existing blocks
    # Modify blocks in original data to use 0-based indexing
    for item in data:
        if "block" in item and item["block"]:
            item["block"] = [(day - 1, hour - 1) for day, hour in item["block"]]

    # Now fill gene without subtracting again
    for item in data:
        if "block" in item and item["block"]:
            for day, hour in item["block"]:
                for sec in item["sections"]:
                    gene[sec][day][hour] = (item["id"], item["subjects"])


    # Run lab allocation
    gene = allocate_labs(gene, data, section_data)

    # Save updated data
    
    # Add lab day as forbidden day for matching theory entries
    for item in data:
        item["forbidden_day"] = -1
    for lab_item in data:
        if lab_item["lab"] > 0:
            lab_sections = lab_item["sections"]
            lab_subjects = lab_item["subjects"]
            lab_day =  lab_item["block"][0][0]

            for theory_item in data:
                if theory_item["theory"] > 0:
                    if theory_item["sections"] == lab_sections and theory_item["subjects"] == lab_subjects:
                        theory_item["forbidden_day"] = lab_day
                        #print(f"Added forbidden day {lab_day} for theory item {theory_item['id']} due to lab item {lab_item['id']}")

    df = pd.DataFrame(data)
    
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(lambda x: ', '.join(map(str, x)) if isinstance(x, list) else x)

    df.to_excel(op_path, index=False)

    #print(f"Lab allocation complete. Saved to: {output_path}")
    #print(f"Data saved to: data/data_lunch_lab_allocated.xlsx")

    with open(data_path, 'wb') as f:
        pickle.dump((data), f)

    return data