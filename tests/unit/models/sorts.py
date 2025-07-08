from src.models.generate_sortings import find_valid_sortings

def test_constraint_solver():
    def run_test(test_name, table, roles, expected_positions=None):
        print(f"Running test: {test_name}")
        result = find_valid_sortings(table, roles)
        
        if isinstance(result, str):
            print(f"  Error: {result}")
            return
        
        if not result:
            print("  No solution found")
            return
        
        perm = result[0]
        print(f"  Solution: {perm}")
        
        if expected_positions:
            positions = {}
            for idx, row in enumerate(perm):
                positions[row] = idx
            for row, expected in expected_positions.items():
                if positions[row] != expected:
                    print(f"  Validation failed: Row {row} at position {positions[row]}, expected {expected}")
                    return
            print("  Validation passed")
        print()

    table1 = [
        [""],
        ["_[0]-3_"],
        ["_[0]_2-"],
        ["_[0]_2_"]
    ]
    roles1 = ['dependencies']
    run_test("Test 1 - Basic after constraint", 
             table1, roles1)

if __name__ == '__main__':
    test_constraint_solver()