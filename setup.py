import subprocess

files = [
    "core.heuristic_base_allocator",
    "core.shared_subjects_section_clusterer",
    "core.dependency_graph",
]

for f in files:
    print(f"Running {f}...")
    subprocess.run(["python", "-m", f])

