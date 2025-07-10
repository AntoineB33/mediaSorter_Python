from networkx import DiGraph, topological_sort, NetworkXUnfeasible, simple_cycles
import os
from ortools.sat.python import cp_model
import re


class SolutionCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self, pos_vars, n, max_solutions):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.pos_vars = pos_vars
        self.n = n
        self.max_solutions = max_solutions
        self.solutions = []
        self.count = 0

    def OnSolutionCallback(self):
        if self.count >= self.max_solutions:
            return
        current_pos = [self.Value(var) for var in self.pos_vars]
        permutation = sorted(range(self.n), key=lambda x: current_pos[x])
        self.solutions.append(permutation)
        self.count += 1
        if self.count >= self.max_solutions:
            self.StopSearch()

    def get_solutions(self):
        return self.solutions
    
def find_valid_sortings0(table):
    import random
    n = len(table)

    # returns table in a random order
    return random.sample(range(n), n)

def find_valid_sortings(table, roles):
    n = len(table)
    
    # Build dependency graph and parse optimization goals
    graph = DiGraph()
    graph.add_nodes_from(range(n))
    dependencies = [[] for _ in range(n)]
    optimization_terms = []
    
    for i in range(n):
        for c, cell in enumerate(table[i]):
            if roles[c] != 'dependencies':
                continue
            entries = cell.split(';')
            for entry in entries:
                match = re.match(r'after\s+([1-9][0-9]*)', entry)
                if match:
                    j = int(match.group(1)) - 1
                    if j >= n or j < 0:
                        return f"Invalid dependency: {entry} in row {i+1}"
                    dependencies[i].append(j)
                    graph.add_edge(j, i)
                else:
                    match = re.match(r'as far as possible from (\d+)', entry)
                    if match:
                        X = int(match.group(1)) - 1
                        if X >= n or X < 0:
                            return f"Invalid optimization term: {entry} in row {i+1}"
                        optimization_terms.append((i, X))
                    elif entry != "":
                        return f"Invalid entry: {entry} in row {i+1}"
    
    # Check if the dependency graph is a DAG
    try:
        topological_order = list(topological_sort(graph))
    except NetworkXUnfeasible:
        # Attempt to find a cycle to report
        try:
            cycle = next(simple_cycles(graph))  # Get the first cycle
            cycle_str = ' -> '.join(map(lambda x: str(x+1), cycle)) + f' -> {cycle[0]+1}'
            return f"The dependency graph contains a cycle: {cycle_str}"
        except StopIteration:
            return "The dependency graph is not a DAG (unexpected error)."
    
    # If no optimization terms, return the topological order
    if not optimization_terms:
        return [topological_order]
    
    # Proceed with CP model to optimize the permutation
    model = cp_model.CpModel()
    pos = [model.NewIntVar(0, n - 1, f'pos_{i}') for i in range(n)]
    model.AddAllDifferent(pos)
    
    # Add dependency constraints
    for i in range(n):
        for j in dependencies[i]:
            model.Add(pos[j] < pos[i])
    
    # Create variables for absolute differences and add to the objective
    diff_vars = []
    for i, X in optimization_terms:
        diff = model.NewIntVar(0, n - 1, f'diff_{i}_{X}')
        model.AddAbsEquality(diff, pos[i] - pos[X])
        diff_vars.append(diff)
    
    # Maximize the sum of all absolute differences
    model.Maximize(sum(diff_vars))
    
    workers = 1
    cpu_available = os.cpu_count()
    if n > 100:
        workers = min(cpu_available, 4)
    if n > 300:
        workers = min(cpu_available, 5)
    if n > 500:
        workers = min(cpu_available, 6)
    if n > 700:
        workers = min(cpu_available, 7)
    if n > 900:
        workers = min(cpu_available, 8)
    if n > 1000:
        workers = min(cpu_available, 16)
            
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Extract the solution
        solution = [solver.Value(pos[i]) for i in range(n)]
        permutation = sorted(range(n), key=lambda x: solution[x])
        return [permutation]
    else:
        return []

def order_table(res, table):
    old_to_new = {old_index: new_index for new_index, old_index in enumerate(res)}
    new_table = []
    for old_index in res:
        original_row = table[old_index]
        new_row = []
        for cell in original_row:
            if isinstance(cell, str):
                updated_cell = re.sub(r'\[(\d+)\]', lambda m: '[' + str(old_to_new[int(m.group(1))]) + ']', cell)
                updated_cell = re.sub(r'as far as possible from (\d+)', lambda m: "as far as possible from " + str(old_to_new[int(m.group(1))]), updated_cell)
                new_row.append(updated_cell)
            else:
                new_row.append(cell)
        new_table.append(new_row)
    return new_table