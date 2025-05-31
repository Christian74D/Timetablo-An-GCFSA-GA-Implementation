import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import pickle
import os
from collections import defaultdict
from core.constants import data_path

# Paths
base = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(base, '..', 'data')
data_file_path = os.path.join(data_folder, 'timetable_data.pkl')
shared_group_path = os.path.join(data_folder, 'shared_subject_groups.pkl')

# Load data
with open(data_file_path, 'rb') as f:
    data = pickle.load(f)

with open(shared_group_path, 'rb') as f:
    shared_subject_groups = pickle.load(f)

# Updating data to include sections
row_info = []
periods_by_id = {}
for row in data:
    rid = row['id']
    row_info.append({
        'id': rid,
        'sections': row['sections'],
        'staffs': set(row['staffs']),
    })
    periods_by_id[rid] = row['theory'] + row['lab']

# SECTION-WISE GRAPH
sections = sorted({sec for row in row_info for sec in row['sections']})
G_sec = nx.Graph()
G_sec.add_nodes_from(sections)
section_pair_ids = defaultdict(set)

for i in range(len(row_info)):
    row_a = row_info[i]
    for j in range(i + 1, len(row_info)):
        row_b = row_info[j]
        if not row_a['staffs'].intersection(row_b['staffs']):
            continue
        for sec_a in row_a['sections']:
            for sec_b in row_b['sections']:
                if sec_a == sec_b:
                    continue
                key = tuple(sorted((sec_a, sec_b)))
                section_pair_ids[key].add(row_a['id'])
                section_pair_ids[key].add(row_b['id'])

for (sec1, sec2), id_set in section_pair_ids.items():
    weight = sum(periods_by_id[rid] for rid in id_set)
    if weight > 0:
        G_sec.add_edge(sec1, sec2, weight=weight)

# Saving graph data
plt.figure(figsize=(10, 8), dpi=600)
pos = nx.spring_layout(G_sec, seed=42)
nx.draw(G_sec, pos, with_labels=True, node_color="lightgreen", node_size=2200, font_size=10)
edge_labels = {(u, v): f"{d['weight']}" for u, v, d in G_sec.edges(data=True)}
nx.draw_networkx_edge_labels(G_sec, pos, edge_labels=edge_labels, font_size=8)
plt.title("Section Dependency Graph (Unique ID-based Period Sum)")
plt.savefig(os.path.join(data_folder, 'dependency_graph.png'), dpi=600)
with open(os.path.join(data_folder, 'dependency_graph.pkl'), 'wb') as f:
    pickle.dump(G_sec, f)

print("Saved section-wise graph.")

# GROUP-WISE GRAPH (clustered)
def format_group_label(group):
    return ",".join(sorted(group))

# Labelling groups using section names
group_labels = [format_group_label(group) for group in shared_subject_groups]
section_to_group = {}
for group in shared_subject_groups:
    label = format_group_label(group)
    for sec in group:
        section_to_group[sec] = label

G_grp = nx.Graph()
for label in group_labels:
    G_grp.add_node(label)

group_pair_weights = defaultdict(int)

# Aggregate weights
for (sec1, sec2), id_set in section_pair_ids.items():
    g1, g2 = section_to_group[sec1], section_to_group[sec2]
    if g1 == g2:
        continue  
    key = tuple(sorted((g1, g2)))
    group_pair_weights[key] += sum(periods_by_id[rid] for rid in id_set)

# Normalize weights
for (g1, g2), weight in group_pair_weights.items():
    size1 = len(g1.split(','))  # sections in group 1
    size2 = len(g2.split(','))  # sections in group 2
    normalized_weight = weight / (size1 * size2)
    G_grp.add_edge(g1, g2, weight=normalized_weight)


# Plot
plt.figure(figsize=(12, 9), dpi=600)
pos = nx.spring_layout(G_grp, seed=42)
nx.draw(G_grp, pos, with_labels=True, node_color="skyblue", node_size=3000, font_size=9)
edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G_grp.edges(data=True)}
nx.draw_networkx_edge_labels(G_grp, pos, edge_labels=edge_labels, font_size=8)
plt.title("Group-wise Dependency Graph (Sections as Group Labels)")
plt.savefig(os.path.join(data_folder, 'group_dependency_graph.png'), dpi=600)
with open(os.path.join(data_folder, 'group_dependency_graph.pkl'), 'wb') as f:
    pickle.dump(G_grp, f)

print("Saved group-wise graph.")
