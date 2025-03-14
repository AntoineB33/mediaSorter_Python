from sort import sort_elements

# Example test case from user
data = [
    [["A1", "A2"], ["appears before B"]],
    [["B"], ["appears after C2", "appears before D"]],
    [["C1", "C2"], []],
    [["D", "E"], []],
]

print("Running test case:")
num_solutions = sort_elements(data, max_solutions=2)
print(f"\nFound {num_solutions} solution(s)")

# Validate solution logic
def validate_solution(solution_order, data):
    name_to_element = {}
    for idx, entry in enumerate(data):
        for name in entry[0]:
            name_to_element[name] = idx

    pos = {idx: order for order, idx in enumerate(solution_order)}
    for element_idx, entry in enumerate(data):
        _, constraints = entry
        for condition in constraints:
            parts = condition.split()
            target_name = parts[2]
            target_element = name_to_element[target_name]
            
            if parts[1] == "before" and pos[element_idx] >= pos[target_element]:
                return False
            if parts[1] == "after" and pos[element_idx] <= pos[target_element]:
                return False
    return True

# Manual validation for the example case
valid_orders = [
    [2, 0, 1, 3],  # C → A → B → D/E
    [2, 0, 3, 1],   # C → A → D/E → B
]

print("\nManual validation:")
for order in valid_orders:
    print(f"Order {order}: {'Valid' if validate_solution(order, data) else 'Invalid'}")