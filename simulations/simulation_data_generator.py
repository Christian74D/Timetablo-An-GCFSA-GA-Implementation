import pandas as pd
import random
import string

# === MASTER CONTROL ===
NUM_SECTIONS = 1  # 👈 Tune this to scale
SUBJECTS_PER_SECTION = 7  # 5 theory + 2 lab
MAX_SUBJECTS_PER_STAFF = 5
BLOCKED_ENTRY_COUNT = 4
BLOCKED_SECTIONS_PER_ENTRY = min(NUM_SECTIONS, random.randint(6, 12))

# Derived constants
NUM_SUBJECTS = 500 #for subject codes
NUM_STAFF = int(NUM_SECTIONS * 3)

# === RANGE LIMITS ===
SUBJ_COUNT_RANGE = (1, 1)
STAFF_COUNT_RANGE = (1, 1)

# === HELPERS ===
def excel_style_labels(n):
    labels = []
    i = 1
    while len(labels) < n:
        label = ""
        x = i
        while x > 0:
            x, r = divmod(x - 1, 26)
            label = chr(65 + r) + label
        labels.append(label)
        i += 1
    return labels

def generate_section_codes():
    return [f"Sec {label}" for label in excel_style_labels(NUM_SECTIONS)]

def generate_subject_codes():
    return [f"XX{label}" for label in excel_style_labels(NUM_SUBJECTS)]

def generate_staff_list():
    return [f"Prof {label}" for label in excel_style_labels(NUM_STAFF)]

# === ENTRY GENERATORS ===
def generate_individual_entries(section_pool, subject_pool, staff_pool, staff_workload, used_subjects, start_id):
    entries = []
    sid = start_id
    for sec in section_pool:
        # Pick 5 theory subjects
        theory_subjects = random.sample([s for s in subject_pool if s not in used_subjects], 5)
        for subj in theory_subjects:
            used_subjects.add(subj)
            eligible_staff = [s for s in staff_pool if staff_workload[s] < MAX_SUBJECTS_PER_STAFF]
            if not eligible_staff:
                raise ValueError("No eligible staff left for theory assignment.")
            staff = random.choice(eligible_staff)
            staff_workload[staff] += 1
            entries.append({
                "id": sid,
                "sections": sec,
                "subjects": subj,
                "staffs": staff,
                "theory": random.randint(3,4),
                "lab": "",
                "block": ""
            })
            sid += 1

        # Pick 2 lab subjects
        lab_subjects = random.sample([s for s in subject_pool if s not in used_subjects], 2)
        for subj in lab_subjects:
            used_subjects.add(subj)
            lab_staffs = random.sample([s for s in staff_pool if staff_workload[s] < MAX_SUBJECTS_PER_STAFF], 4)
            for staff in lab_staffs:
                staff_workload[staff] += 1
            entries.append({
                "id": sid,
                "sections": sec,
                "subjects": subj,
                "staffs": ", ".join(lab_staffs),
                "theory": "",
                "lab": 2,
                "block": ""
            })
            sid += 1
    return entries, sid

def generate_group_entries(section_pool, subject_pool, staff_pool, staff_workload, used_subjects, start_id):
    entries = []
    sid = start_id
    available_sections = section_pool[:]
    random.shuffle(available_sections)

    while available_sections:
        group_size = random.randint(1, max(1, NUM_SECTIONS // 4))
        cluster = available_sections[:group_size]
        available_sections = available_sections[group_size:]

        subj = random.choice([s for s in subject_pool if s not in used_subjects])
        used_subjects.add(subj)
        staff_group = random.sample([s for s in staff_pool if staff_workload[s] < MAX_SUBJECTS_PER_STAFF], len(cluster))
        for staff in staff_group:
            staff_workload[staff] += 1

        entries.append({
            "id": sid,
            "sections": ", ".join(cluster),
            "subjects": subj,
            "staffs": ", ".join(staff_group),
            "theory": random.randint(2, 4),
            "lab": "",
            "block": ""
        })
        sid += 1

        if random.choice([True, False]):  # also assign lab for group subject
            subj_lab = random.choice([s for s in subject_pool if s not in used_subjects])
            used_subjects.add(subj_lab)
            lab_staffs = random.sample([s for s in staff_pool if staff_workload[s] < MAX_SUBJECTS_PER_STAFF], len(cluster))
            for staff in lab_staffs:
                staff_workload[staff] += 1
            entries.append({
                "id": sid,
                "sections": ", ".join(cluster),
                "subjects": subj_lab,
                "staffs": ", ".join(lab_staffs),
                "theory": "",
                "lab": 2,
                "block": ""
            })
            sid += 1

    return entries, sid

def generate_blocked_entries(section_pool, start_id):
    blocked_entries = []
    allowed_hours = [1, 2, 7, 8]
    used_slots = set()

    for i in range(start_id, start_id + BLOCKED_ENTRY_COUNT):
        sections = random.sample(section_pool, BLOCKED_SECTIONS_PER_ENTRY)
        block_slots = set()

        while len(block_slots) < 1:
            slot = (random.randint(1, 5), random.choice(allowed_hours))
            if slot not in used_slots:
                used_slots.add(slot)
                block_slots.add(slot)

        blocked_entries.append({
            "id": i,
            "sections": ", ".join(sections),
            "subjects": f"BLOCKED_{i}",
            "staffs": "",
            "theory": "",
            "lab": "",
            "block": ", ".join(f"({d}, {h})" for d, h in sorted(block_slots))
        })
    return blocked_entries

# === RUN GENERATOR ===
section_pool = generate_section_codes()
subject_pool = generate_subject_codes()
staff_pool = generate_staff_list()
staff_workload = {s: 0 for s in staff_pool}
used_subjects = set()

next_id = 1
individual_entries, next_id = generate_individual_entries(
    section_pool, subject_pool, staff_pool, staff_workload, used_subjects, next_id)

group_entries, next_id = generate_group_entries(
    section_pool, subject_pool, staff_pool, staff_workload, used_subjects, next_id)

blocked_entries = generate_blocked_entries(section_pool, next_id)

# === SAVE TO FILE ===
all_entries = individual_entries + group_entries + blocked_entries
df = pd.DataFrame(all_entries)
print(df)
filename = f"simulations/synthetic_data_{NUM_SECTIONS}.xlsx"
df.to_excel(filename, index=False)
print(f"✅ Anonymized data generated → Saved to '{filename}'")
