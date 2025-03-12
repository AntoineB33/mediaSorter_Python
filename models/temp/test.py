import random
from sort import sort_elements

def generate_test_case(num_elements=4):
    """Generate a test case with random constraints compatible with a random base order."""
    elements = [chr(ord('A') + i) for i in range(num_elements)]
    base_order = elements.copy()
    random.shuffle(base_order)
    
    data = []
    constraints = {element: [] for element in elements}
    
    # Generate constraints for each element based on the base order
    for idx, element in enumerate(base_order):
        # Elements that come after (for "before" constraints)
        after_elements = base_order[idx+1:]
        # Elements that come before (for "after" constraints)
        before_elements = base_order[:idx]
        
        # Add up to 2 "before" constraints
        for target in random.sample(after_elements, min(2, len(after_elements))):
            constraints[element].append(f"appears before {target}")
        
        # Add up to 2 "after" constraints
        for target in random.sample(before_elements, min(2, len(before_elements))):
            constraints[element].append(f"appears after {target}")
    
    # Build the data structure
    for element in elements:
        data.append([element, constraints[element]])
    
    return data

def validate_solution(solution, data):
    """Check if the solution satisfies all constraints."""
    if not solution:
        return False
    pos = {name: idx for idx, name in enumerate(solution)}
    for entry in data:
        name = entry[0]
        for condition in entry[1]:
            parts = condition.split()
            other = parts[2]
            if parts[1] == "before" and pos[name] >= pos[other]:
                return False
            elif parts[1] == "after" and pos[name] <= pos[other]:
                return False
    return True

def run_tests(num_tests=10):
    """Run multiple test cases and validate results."""
    for test_idx in range(num_tests):
        print(f"\n=== Test Case {test_idx + 1} ===")
        data = generate_test_case()
        print("Constraints:")
        for entry in data:
            print(f"  {entry[0]}: {', '.join(entry[1]) or 'None'}")
        
        solution = sort_elements(data)
        if solution and validate_solution(solution, data):
            print(f"Solution: {' → '.join(solution)}")
            print("✅ Valid solution")
        else:
            print("❌ No valid solution found (this should not happen)")

if __name__ == "__main__":
    run_tests()