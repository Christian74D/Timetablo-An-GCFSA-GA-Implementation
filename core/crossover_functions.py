import random
import pickle
import heapq  # for weighted BFS priority queue
import os
from random import choices

with open('data/shared_subject_groups.pkl', 'rb') as f:
    subject_groups = pickle.load(f)

with open('data/group_dependency_graph.pkl', 'rb') as f:
    group_graph = pickle.load(f)


def format_group_label(group):
    return ",".join(sorted(group))

def get_group_map(groups):
    group_map = {}
    for group in groups:
        for section in group:
            group_map[section] = frozenset(group)
    return group_map


def crossover_random(parent1, parent2):
    groups = [frozenset(g) for g in subject_groups]
    group_map = get_group_map(groups)
    selected = set(random.sample(groups, k=random.randint(1, len(groups) // 2)))

    child1, child2 = {}, {}
    assigned = set()
    
    for group in groups:
        target = parent1 if group in selected else parent2
        alt = parent2 if group in selected else parent1
        for sec in group:
            if sec not in assigned:
                child1[sec] = [row.copy() for row in target[sec]]
                child2[sec] = [row.copy() for row in alt[sec]]
                assigned.add(sec)

    return child1, child2

def crossover_biological(parent1, parent2):
    groups = [frozenset(g) for g in subject_groups]
    group_map = get_group_map(groups)
    point = random.randint(1, len(groups) - 1)
    selected = set(groups[:point])

    child1, child2 = {}, {}
    assigned = set()

    for group in groups:
        target = parent1 if group in selected else parent2
        alt = parent2 if group in selected else parent1
        for sec in group:
            if sec not in assigned:
                child1[sec] = [row.copy() for row in target[sec]]
                child2[sec] = [row.copy() for row in alt[sec]]
                assigned.add(sec)

    return child1, child2

def crossover_graph_based(parent1, parent2):
    # Create section -> group label map
    group_map = {sec: format_group_label(group) for group in subject_groups for sec in group}
    all_groups = [format_group_label(group) for group in subject_groups]

    visited = set()
    selected = set()

    # Start from a random node
    queue = [random.choice(list(group_graph.nodes))]

    while queue and len(visited) < len(group_graph.nodes) // 2:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        selected.add(current)

        neighbors = [n for n in group_graph.neighbors(current) if n not in visited]
        if not neighbors:
            continue

        weights = [group_graph.edges[current, n].get("weight", 1) for n in neighbors]
        total = sum(weights)

        if total == 0:
            # if all weights are zero, pick a random neighbor
            next_nodes = [random.choice(neighbors)]
        else:
            probs = [w / total for w in weights]
            next_nodes = choices(neighbors, weights=probs, k=1)  #Choosing one node

        queue.extend(next_nodes)


    # Build children based on selected groups
    child1, child2 = {}, {}
    assigned = set()
    #print("Selected groups:", selected)

    for group in subject_groups:
        label = format_group_label(group)
        source, alt = (parent1, parent2) if label in selected else (parent2, parent1)

        for sec in group:
            if sec not in assigned:
                child1[sec] = [row.copy() for row in source[sec]]
                child2[sec] = [row.copy() for row in alt[sec]]
                assigned.add(sec)

    return child1, child2
