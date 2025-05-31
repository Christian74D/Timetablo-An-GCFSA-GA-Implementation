import random
from copy import deepcopy
from core.constants import HOURS, DAYS

def get_conflict_free_slots(gene, sections, subject_id, subject_staff, staff_by_id):
    conflict_free_slots = {}
    for day in range(DAYS):
        free_hours = [hour for hour in range(HOURS) if all(gene[sec][day][hour] is None for sec in sections)]
        random.shuffle(free_hours)
        for hour in free_hours:
            staff_in_hour = set()
            for sec in gene:
                cell = gene[sec][day][hour]
                if cell:
                    other_id = cell[0]
                    staff_in_hour |= staff_by_id[other_id]
            if subject_staff.isdisjoint(staff_in_hour):
                conflict_free_slots[day] = hour
                break  # only one period per day per subject
    return conflict_free_slots

def mutate_gene_GCFSA(data, gene, mutation_rate): # Greedy Conflict-Free Slot Assignment (GCFSA)
    gene = deepcopy(gene)
    staff_by_id = {item["id"]: set(item["staffs"]) for item in data}

    for item in data:
        if (item.get("block") is not None or item["theory"] == 0):
            continue

        subject_id = item["id"]
        subject_staff = staff_by_id[subject_id]
        sections = item["sections"]
        current_periods = [
            (day, hour)
            for day in range(DAYS)
            for hour in range(HOURS)
            if all(
                gene[sec][day][hour] is not None and gene[sec][day][hour][0] == subject_id
                for sec in sections
            )
        ]

        required_slots = item["theory"]
      

        for (day, hour) in current_periods:
            for sec in sections:
                gene[sec][day][hour] = None

        # Trying conflict-free allocation
        conflict_free_slots = get_conflict_free_slots(gene, sections, subject_id, subject_staff, staff_by_id)
        chosen_slots = [(day, hour) for day, hour in conflict_free_slots.items()]
        chosen_slots = [slot for slot in chosen_slots if slot[0] != item["forbidden_day"]]
        chosen_slots = chosen_slots[:required_slots]
        used_days = set(conflict_free_slots.keys())
        used_days.add(item["forbidden_day"])
        if len(chosen_slots) < required_slots:
            #print(f"[{len(chosen_slots)}/{required_slots}]")
            #print(f"id {subject_id} sections {sections} staff {subject_staff}")

        
            candidate_days = [d for d in range(DAYS) if d not in used_days]
            random.shuffle(candidate_days)
            i = 0
            while len(chosen_slots) < required_slots and i < len(candidate_days):
                day = candidate_days[i]
                i += 1
                free_hours = [
                    hour for hour in range(HOURS)
                    if all(gene[sec][day][hour] is None for sec in sections)
                ]
                if free_hours:
                    hour = random.choice(free_hours)
                    chosen_slots.append((day, hour))
             

            
             

        # Update gene
        for (day, hour) in chosen_slots:
            for sec in sections:
                gene[sec][day][hour] = (subject_id, item["subjects"])
        item["period"] = chosen_slots

    return gene


def mutate_gene(data, gene, mutation_rate):
    gene = deepcopy(gene)  
    for item in data:
        if item.get("block") is not None or item["theory"] == 0 or random.random() > mutation_rate:
            continue

        subject_id = item["id"]
        sections = item["sections"]
        current_periods = item.get("period", [])

        # Current days
        used_days = {day for (day, _) in current_periods}

        # Free current slots
        for (day, hour) in current_periods:
            for sec in sections:
                gene[sec][day][hour] = None

        # Available slots
        free_slots_per_day = {
            day: [
                hour for hour in range(HOURS)
                if all(gene[sec][day][hour] is None for sec in sections)
            ]
            for day in range(DAYS)
        }
        
        valid_days = [d for d in free_slots_per_day if free_slots_per_day[d]]
        if item["forbidden_day"] > 1:
                    valid_days = [day for day in valid_days if day != item["forbidden_day"]]
        chosen_days = random.sample(valid_days, len(current_periods))
        new_periods = []

        for day in chosen_days:
            hour = random.choice(free_slots_per_day[day])
            for sec in sections:
                gene[sec][day][hour] = (subject_id, item["subjects"])
            new_periods.append((day, hour))
        item["period"] = new_periods
    
    return gene


