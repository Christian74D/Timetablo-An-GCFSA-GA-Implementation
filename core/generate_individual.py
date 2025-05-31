import random
from copy import deepcopy
from core.constants import HOURS, DAYS, allocation_attempts, ImpossibleAllocationError

def generate_gene(data, section_data, heuristic=False):
    def initialize_with_blocks(data_copy):
        gene = {
            sec: [[None for _ in range(HOURS)] for _ in range(DAYS)]
            for sec in section_data
        }
        #for i in data:
        #    print(i)

        free_slots = {
            sec: {(day, hour) for day in range(DAYS) for hour in range(HOURS)}
            for sec in section_data
        }

        for item in data_copy:
            if item["block"] is not None:
                for day, hour in item["block"]:
                    for sec in item["sections"]:
                        gene[sec][day][hour] = (item["id"], item["subjects"])
                        free_slots[sec].remove((day, hour))
                item["period"] = item["block"]

        return gene, free_slots

    prefilled_data = deepcopy(data)
    prefilled_gene, prefilled_slots = initialize_with_blocks(deepcopy(prefilled_data))

    for attempt in range(1, allocation_attempts + 1):
        data_attempt = deepcopy(prefilled_data)
        gene = deepcopy(prefilled_gene)
        free_slots = deepcopy(prefilled_slots)
        success = True

        for item in data_attempt:
            if item["block"] is None:
                theory = item["theory"]
                sections = item["sections"]

                free_slots_per_day = {
                    day: [
                        hour for hour in range(HOURS)
                        if all((day, hour) in free_slots[sec] for sec in sections)
                    ]
                    for day in range(DAYS)
                }

                valid_days = [day for day, hours in free_slots_per_day.items() if hours]
                if item["forbidden_day"] > 1:
                    valid_days = [day for day in valid_days if day != item["forbidden_day"]]

                if len(valid_days) < theory:
                    success = False
                    break

                try:
                    chosen_days = random.sample(valid_days, theory)
                except ValueError:
                    success = False
                    break

                assigned_periods = []

                for day in chosen_days:
                    available_hours = free_slots_per_day[day]
                    if not available_hours:
                        success = False
                        break

                    hour = random.choice(available_hours)

                    if all((day, hour) in free_slots[sec] for sec in sections):
                        for sec in sections:
                            gene[sec][day][hour] = (item["id"], item["subjects"])
                            free_slots[sec].remove((day, hour))
                        assigned_periods.append((day, hour))
                    else:
                        success = False
                        break

                if not success:
                    break

                item["period"] = assigned_periods

        if success:
            #print(f":) Full Lab allocation succeeded on attempt {attempt}")
            data[:] = data_attempt
            if heuristic:
                return attempt
            return gene

    #print(f":( Individual generation failed after {allocation_attempts} attempts")
    raise ImpossibleAllocationError(f"Allocation failed after {allocation_attempts} attempts.")
    return None
