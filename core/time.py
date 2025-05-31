def calculate_time(start, end):
    total_time = end - start
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int(total_time % 60)
    return f"Total Time: {hours} hours, {minutes} minutes, {seconds} seconds"

def save_time_to_file(time_str, filename="outputs/time.txt"):
    with open(filename, "w") as file:
        file.write(time_str)
    print("Time saved to time.txt")