from src.models.generate_sortings import ConstraintSorter

# Example usage:
if __name__ == "__main__":
    # Example with elements A, B, C, D, E, F, G, H, I, J
    elements = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    sorter = ConstraintSorter(elements)
    
    # Example constraints:
    # Element A cannot be in intervals [-10,-6], [-2, 4], [7, end] around element B
    sorter.add_forbidden_constraint('B', 'A', [(-float('inf'), 4), (6, float('inf'))])
    
    # Element C cannot be in interval [-3, 2] around element D
    sorter.add_forbidden_constraint('C', 'D', [(-3, 2)])
    
    # Maximize distance between A and E
    sorter.add_maximize_distance_constraint('A', 'E')
    
    # Maximize distance between B and C
    sorter.add_maximize_distance_constraint('B', 'C')
    
    # Solve the problem
    print("Solving constraint-based sorting problem...")
    solution = sorter.solve(max_attempts=50, max_iterations=2000)
    
    if solution:
        print(f"Solution found: {solution}")
        print(f"Is valid: {sorter.is_valid_placement(solution)}")
        print(f"Distance score: {sorter.calculate_distance_score(solution)}")
        
        # Show positions for clarity
        print("\nPositions:")
        for i, elem in enumerate(solution):
            print(f"Position {i}: {elem}")
    else:
        print("No valid solution found!")