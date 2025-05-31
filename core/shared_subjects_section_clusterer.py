import os
import pickle
from collections import defaultdict

# Load data
base = os.getcwd()
data_folder = os.path.join(base, 'data')
data_file_path = os.path.join(data_folder, 'timetable_data.pkl')

with open(data_file_path, 'rb') as f:
    data = pickle.load(f)

# Mapping subject ID to sections
subject_to_sections = defaultdict(set)

all_sections = set()  

for row in data:
    for section in row['sections']:
        all_sections.add(section)  
    if row['theory'] > 0:
        subject_to_sections[row['id']].update(row['sections'])

# Union for sections sharing subjects
parent = {}

def find(x):
    parent.setdefault(x, x)
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]

def union(x, y):
    parent[find(x)] = find(y)

for sections in subject_to_sections.values():
    sections = list(sections)
    for i in range(len(sections) - 1):
        union(sections[i], sections[i + 1])

for sec in all_sections:
    find(sec)

# init groups
groups = defaultdict(set)
for section in all_sections:
    root = find(section)
    groups[root].add(section)

# List of sets
shared_subject_groups = list(groups.values())

# Save
shared_subject_groups_path = os.path.join(data_folder, 'shared_subject_groups.pkl')
with open(shared_subject_groups_path, 'wb') as f:
    pickle.dump(shared_subject_groups, f)

print(shared_subject_groups)
print(f"Shared subject groups saved to {shared_subject_groups_path}")
print(f"Number of groups: {len(shared_subject_groups)}")
