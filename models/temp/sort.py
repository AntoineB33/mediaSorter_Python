from ortools.sat.python import cp_model

def sort_elements(data, total_length=10):
    """Sort elements based on given constraints using CP-SAT.
    
    Args:
        data: List of elements with their constraints, e.g.,
            [["A", ["appears before B"]], ["B", ["appears after C"]], ...]
        total_length: Maximum position value (default 10).
        
    Returns:
        Sorted list of elements if a solution exists, otherwise None.
    """
    model = cp_model.CpModel()
    variables = {}
    
    # Create variables for each element
    for entry in data:
        name = entry[0]
        variables[name] = model.NewIntVar(0, total_length - 1, name)
    
    # All elements must have distinct positions
    model.AddAllDifferent(variables.values())
    
    # Add constraints for each element
    for entry in data:
        name = entry[0]
        constraints = entry[1]
        for condition in constraints:
            parts = condition.split()
            relation = parts[1]  # "before" or "after"
            other_element = parts[2]
            if relation == "before":
                model.Add(variables[name] < variables[other_element])
            elif relation == "after":
                model.Add(variables[name] > variables[other_element])
    
    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        return sorted(variables.keys(), key=lambda x: solver.Value(variables[x]))
    else:
        return None