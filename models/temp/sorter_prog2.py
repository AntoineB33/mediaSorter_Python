import random

def validate_table(permutation, table):
    for i, row in enumerate(table):
        # Get the index of the current element in the permutation
        current_index = permutation.index(i)
        
        # Check if all elements in the row are before the current element in the permutation
        for element in row:
            if permutation.index(element) >= current_index:
                return False
    return True

# Example usage:
n = random.randint(1, 500)
permutation = list(range(n))
random.shuffle(permutation)

table = [[] for _ in range(n)]
for sorting_index in range(n):
    predecessors = permutation[:sorting_index]
    k = random.randint(0, sorting_index)
    row = random.sample(predecessors, k) if k else []
    row = ["after " + str(element) for element in row]
    table[permutation[sorting_index]] = row

print(f"Random n: {n}")
print(f"Shuffled list: {permutation}\n")
print("Table of random preceding elements:")
for i, row in enumerate(table):
    print(f"Row {i} (Element {i}): {sorted(row)}")

# Validate the table
is_valid = validate_table(permutation, table)
print(f"\nIs the table valid? {is_valid}")