from generate_sortings import find_valid_sortings
import threading

def compute_and_print_sorting(table):
    sorting = find_valid_sortings(table)
    print("Sorting result:", sorting)

print("hello")
table = [[] for i in range(50)]
table[0] = ["after 1", "as far as possible from 1"]

# Start the sorting computation in a background thread
thread = threading.Thread(target=compute_and_print_sorting, args=(table,))
thread.start()

print("world")
print("end of code")