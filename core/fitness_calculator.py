from collections import defaultdict
from core.constants import DAYS, HOURS

def build_data_by_id(data):
    return {entry['id']: entry for entry in data}

def count_teacher_conflicts(gene, data_by_id):
    conflicts = 0
    sections = list(gene.keys())

    for day in range(DAYS):
        for period in range(HOURS):
            staff_to_sections = defaultdict(set)

            for section in sections:
                slot = gene[section][day][period]
                if slot is None:
                    continue

                entry_id, _ = slot
                curr = data_by_id.get(entry_id, {})
                staff_list = curr.get('staffs', [])
                for staff in staff_list:
                    if staff == "nan":
                        continue
                    staff_to_sections[staff].add(entry_id)

            for staff, sec_list in staff_to_sections.items():
                if len(sec_list) > 1:
                    #print(f"Conflict detected for staff {staff} on day {day}, period {period}: {sec_list}")
                    conflicts += len(sec_list) - 1  # One is OK, rest are conflicts
            
            #print(f"Day {day}, Period {period}: Staff to Sections: {staff_to_sections}")

    return conflicts

def fitness(gene, data):
    data_by_id = build_data_by_id(data)
    return count_teacher_conflicts(gene, data_by_id)
