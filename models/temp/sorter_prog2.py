import random

# Generate random n and shuffled list
n = random.randint(1, 5)
permutation = list(range(n))
random.shuffle(permutation)

# Create the table of preceding elements
table = [[] for _ in range(n)]
for sorting_index in range(n):
    # Get all elements before
    predecessors = permutation[:sorting_index]
    
    # Randomly choose how many predecessors to include (0 to all)
    k = random.randint(0, sorting_index)
    
    # Randomly select k predecessors (without replacement)
    row = random.sample(predecessors, k) if k else []
    
    table[permutation[sorting_index]] = row

# Print results
print(f"Random n: {n}")
print(f"Shuffled list: {permutation}\n")
print("Table of random preceding elements:")
for i, row in enumerate(table):
    print(f"Row {i} (Element {i}): {sorted(row)}")