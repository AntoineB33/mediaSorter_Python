from ortools.sat.python import cp_model

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""
    def __init__(self, variables, element_names, limit=2):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._variables = variables
        self._element_names = element_names
        self._solution_count = 0
        self._solution_limit = limit

    def on_solution_callback(self):
        self._solution_count += 1
        sorted_elements = sorted(
            range(len(self._variables)),
            key=lambda x: self.Value(self._variables[x])
        )
        print(f"Solution {self._solution_count}: {' → '.join(map(str, sorted_elements))}")
        if self._solution_count >= self._solution_limit:
            self.StopSearch()

    def solution_count(self):
        return self._solution_count

def sort_elements(data, total_length=10, max_solutions=2):
    """Sort elements (which may have multiple names) based on constraints.
    
    Args:
        data: List of elements with names and constraints.
        total_length: Maximum position value.
        max_solutions: Maximum number of solutions to return.
        
    Returns:
        List of solutions (each solution is a list of element indices in order)
    """
    # Create name-to-element mapping
    name_to_element = {}
    for idx, entry in enumerate(data):
        for name in entry[0]:
            name_to_element[name] = idx

    model = cp_model.CpModel()
    num_elements = len(data)
    positions = [model.NewIntVar(0, total_length - 1, f"pos_{i}") for i in range(num_elements)]

    # All elements have distinct positions
    model.AddAllDifferent(positions)

    # Add constraints
    for element_idx, entry in enumerate(data):
        _, constraints = entry
        for condition in constraints:
            parts = condition.split()
            target_name = parts[2]
            
            # Find which element contains the target name
            target_element = name_to_element.get(target_name, None)
            if target_element is None:
                continue  # Skip invalid constraints

            if parts[1] == "before":
                model.Add(positions[element_idx] < positions[target_element])
            elif parts[1] == "after":
                model.Add(positions[element_idx] > positions[target_element])

    # Collect solutions
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter(positions, [entry[0] for entry in data], max_solutions)
    solver.parameters.enumerate_all_solutions = True
    solver.Solve(model, solution_printer)
    
    return solution_printer.solution_count()