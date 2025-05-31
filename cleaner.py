import os
from collections import defaultdict

def clean_generated_files():
    folders = [
        "data/content",
        "generated_timetables/staff",
        "generated_timetables/student"
    ]

    total_deleted = 0
    ext_counter = defaultdict(int)

    for folder in folders:
        if not os.path.exists(folder):
            print(f"[Skipped] Folder not found: {folder}")
            continue

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                ext = os.path.splitext(filename)[-1].lower()
                try:
                    os.remove(file_path)
                    ext_counter[ext] += 1
                    total_deleted += 1
                except Exception as e:
                    print(f"[Error] Could not delete {file_path}: {e}")

    print(f"\n✅ Deleted {total_deleted} files total.")
    for ext, count in ext_counter.items():
        print(f"   - {ext or '[no extension]'}: {count} file(s)")

if __name__ == "__main__":
    clean_generated_files()
    print("Cleaned up generated files.")