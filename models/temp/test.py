import random
from generate_sortings import find_valid_sortings

NUMBER_OF_TESTS = 10
TABLE_SIZE_LIMIT = 500
TABLE_SIZE_MIN = 1

def validate_table(permutation, table):
    for i, row in enumerate(table):
        # Get the index of the current element in the permutation
        current_index = permutation.index(i)
        
        # Check if all elements in the row are before the current element in the permutation
        for element in row:
            if element.startswith("after"):
                j = int(element.split()[1])
                if permutation.index(j) >= current_index:
                    return False
    return True

def print_table(table):
    print("Table of random preceding elements:")
    for i, row in enumerate(table):
        print(f"Element {i}: {sorted(row)}")

for test_num in range(NUMBER_OF_TESTS):
    print(f"Test {test_num + 1}")
    # Example usage:
    n = random.randint(TABLE_SIZE_MIN, TABLE_SIZE_LIMIT)
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
    # print("Table of random preceding elements:")
    # for i, row in enumerate(table):
    #     print(f"Row {i} (Element {i}): {sorted(row)}")

    solutions = find_valid_sortings(table, 2)

    if not solutions:
        print_table(table)
        print("\nNo valid sortings found.")
        break
    for i, solution in enumerate(solutions):
        print(f"\nSolution {i}: {solution}")
        # Validate the table
        is_valid = validate_table(solution, table)
        print(f"\nIs the solution valid? {is_valid}")
        if not is_valid:
            print_table(table)
            break
print("End of test\n")