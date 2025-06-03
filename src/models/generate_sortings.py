from networkx import DiGraph, topological_sort, NetworkXUnfeasible, simple_cycles
import os
from ortools.sat.python import cp_model

import re
def reduce_redundancy(table):
    """
    Reduces redundancy in the dependency table by removing implied constraints.
    For example, if 3 must come after 1 and 1 must come after 2, the constraint
    "3 must come after 2" is redundant and removed.
    """
    n = len(table)
    # Build the dependency graph: graph[i] contains direct dependencies of i
    graph = {i: set() for i in range(n)}
    for i in range(n):
        for entry in table[i]:
            if entry.startswith("after "):
                j = int(entry.split()[1]) + 1
                graph[i].add(j)  # Edge: j -> i (i must come after j)

    # Compute ancestors for each node (all nodes that must come before it)
    ancestors = {i: set() for i in range(n)}
    for i in range(n):
        visited = set()
        stack = [i]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                # Traverse dependencies (edges j -> node)
                for dependency in graph[node]:
                    if dependency not in visited:
                        stack.append(dependency)
        ancestors[i] = visited

    # Remove redundant dependencies
    reduced_table = [[] for _ in range(n)]
    for X in range(n):
        dependencies = list(graph[X])
        non_redundant = []
        for Z in dependencies:
            # Check if Z is implied by other dependencies
            redundant = False
            # Check all other dependencies Y != Z
            for Y in dependencies:
                if Y == Z:
                    continue
                if Z in ancestors[Y]:
                    redundant = True
                    break
            if not redundant:
                non_redundant.append(f"after {Z}")
        reduced_table[X] = non_redundant

    return reduced_table

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

def find_valid_sortings(table):
    n = len(table)
    
    # Build dependency graph and parse optimization goals
    graph = DiGraph()
    graph.add_nodes_from(range(n))
    dependencies = [[] for _ in range(n)]
    optimization_terms = []
    
    for i in range(n):
        for entry in table[i]:
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
                else:
                    return f"Invalid entry: {entry} in row {i+1}"
    
    # Check if the dependency graph is a DAG
    try:
        topological_order = list(topological_sort(graph))
    except NetworkXUnfeasible:
        # Attempt to find a cycle to report
        try:
            cycle = next(simple_cycles(graph))  # Get the first cycle
            cycle_str = ' -> '.join(map(str, cycle)) + f' -> {cycle[0]}'
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