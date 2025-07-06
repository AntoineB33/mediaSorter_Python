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

    # Test 1: Basic after constraint
    table1 = [
        [""],
        ["[1]_2-"],  # Row1 must be at least 1 after Row0
        [""]   # Row2 must be at least 1 after Row0
    ]
    roles1 = ['dependencies']
    run_test("Test 1 - Basic after constraint", 
             table1, roles1,
             {0: 0})  # Row0 must be first

    # Test 2: Discrete positions before
    table2 = [
        [""],
        ["-[1]_2-"],  # Row1 must be 1 or 2 positions before Row0
        ["_[1]-"]
    ]
    roles2 = ['dependencies']
    run_test("Test 2 - Discrete positions before", 
             table2, roles2)

    # Test 3: Range constraints
    table3 = [
        [""],
        [""],
        ["_3_[1]_2-4_"]  # Row2 must be 1-2 before or 3-4 after Row1
    ]
    roles3 = ['dependencies']
    run_test("Test 3 - Range constraints", 
             table3, roles3)

    # Test 4: Complex constraint
    table4 = [
        [""],
        [""],
        ["_3-1_5_[1]_2_4-"]  # Row2: 1-3 before, 5 before, 2 after, 4+ after
    ]
    roles4 = ['dependencies']
    run_test("Test 4 - Complex constraint", 
             table4, roles4)

    # Test 5: Self-reference (should error)
    table5 = [
        ["[1]"],
    ]
    roles5 = ['dependencies']
    run_test("Test 5 - Self-reference", 
             table5, roles5)

    # Test 6: Invalid reference
    table6 = [
        [""],
        ["[3]_1-"]  # Invalid reference (only 2 rows)
    ]
    roles6 = ['dependencies']
    run_test("Test 6 - Invalid reference", 
             table6, roles6)

    # Test 7: Conflicting constraints
    table7 = [
        [""],
        ["[2]_1-"],  # Row1 ≥1 after Row2
        ["[1]_1-"]   # Row2 ≥1 after Row1 → impossible
    ]
    roles7 = ['dependencies']
    run_test("Test 7 - Conflicting constraints", 
             table7, roles7)

    # Test 8: Combined constraints
    table8 = [
        [""],
        ["[1]_1-"],       # Row1 ≥1 after Row0
        ["_1_[1]_2-"]    # Row2: 1 before or ≥2 after
    ]
    roles8 = ['dependencies']
    run_test("Test 8 - Combined constraints", 
             table8, roles8)

if __name__ == '__main__':
    test_constraint_solver()