from networkx import DiGraph, topological_sort, NetworkXUnfeasible, simple_cycles
import os
from ortools.sat.python import cp_model
import re

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

def find_valid_sortings(table, roles):
    n = len(table)
    
    # Create CP model and position variables
    model = cp_model.CpModel()
    pos = [model.NewIntVar(0, n - 1, f'pos_{i}') for i in range(n)]
    model.AddAllDifferent(pos)
    
    # Parse dependency constraints
    for i in range(n):
        for c, cell in enumerate(table[i]):
            if roles[c] != 'dependencies':
                continue
                
            entries = cell.split(';')
            for entry in entries:
                entry = entry.strip()
                if not entry:
                    continue
                    
                # Extract reference row
                ref_match = re.search(r'\[(\d+)\]', entry)
                if not ref_match:
                    return f"Missing reference row in constraint: {entry} in row {i+1}"
                ref_row = int(ref_match.group(1)) - 1  # Convert to 0-indexed
                
                # Validate reference row
                if ref_row < 0 or ref_row >= n:
                    return f"Invalid reference row {ref_row+1} in constraint: {entry} in row {i+1}"
                if ref_row == i:
                    return f"Constraint in row {i+1} refers to itself"
                
                # Split constraint into tokens
                try:
                    tokens = [tok for tok in entry.strip('_').split('_') if tok]
                    ref_token = f'[{ref_match.group(1)}]'
                    ref_idx = tokens.index(ref_token)
                except (ValueError, IndexError):
                    return f"Malformed constraint: {entry} in row {i+1}"
                
                left_tokens = tokens[:ref_idx]
                right_tokens = tokens[ref_idx+1:]
                
                # Process tokens
                condition_vars = []
                d = model.NewIntVar(-n+1, n-1, f'd_{i}_{ref_row}')
                model.Add(d == pos[i] - pos[ref_row])
                
                # Process left tokens (negative offsets)
                for token in left_tokens:
                    if token.endswith('-'):
                        # Half-line constraint (d <= -X)
                        try:
                            x = int(token.rstrip('-'))
                            b = model.NewBoolVar(f'left_hl_{i}_{ref_row}_{x}')
                            model.Add(d <= -x).OnlyEnforceIf(b)
                            condition_vars.append(b)
                        except ValueError:
                            return f"Invalid number in token: {token} in row {i+1}"
                    elif '-' in token:
                        # Range constraint (a-b -> d in [-b, -a])
                        try:
                            a, b = map(int, token.split('-'))
                            low, high = min(a, b), max(a, b)
                            b_var = model.NewBoolVar(f'left_rg_{i}_{ref_row}_{low}_{high}')
                            model.Add(d >= -high).OnlyEnforceIf(b_var)
                            model.Add(d <= -low).OnlyEnforceIf(b_var)
                            condition_vars.append(b_var)
                        except ValueError:
                            return f"Invalid range in token: {token} in row {i+1}"
                    else:
                        # Discrete value (d == -X)
                        try:
                            x = int(token)
                            b = model.NewBoolVar(f'left_dc_{i}_{ref_row}_{x}')
                            model.Add(d == -x).OnlyEnforceIf(b)
                            condition_vars.append(b)
                        except ValueError:
                            return f"Invalid number in token: {token} in row {i+1}"
                
                # Process right tokens (positive offsets)
                for token in right_tokens:
                    if token.endswith('-'):
                        # Half-line constraint (d >= X)
                        try:
                            x = int(token.rstrip('-'))
                            b = model.NewBoolVar(f'right_hl_{i}_{ref_row}_{x}')
                            model.Add(d >= x).OnlyEnforceIf(b)
                            condition_vars.append(b)
                        except ValueError:
                            return f"Invalid number in token: {token} in row {i+1}"
                    elif '-' in token:
                        # Range constraint (a-b -> d in [a, b])
                        try:
                            a, b = map(int, token.split('-'))
                            low, high = min(a, b), max(a, b)
                            b_var = model.NewBoolVar(f'right_rg_{i}_{ref_row}_{low}_{high}')
                            model.Add(d >= low).OnlyEnforceIf(b_var)
                            model.Add(d <= high).OnlyEnforceIf(b_var)
                            condition_vars.append(b_var)
                        except ValueError:
                            return f"Invalid range in token: {token} in row {i+1}"
                    else:
                        # Discrete value (d == X)
                        try:
                            x = int(token)
                            b = model.NewBoolVar(f'right_dc_{i}_{ref_row}_{x}')
                            model.Add(d == x).OnlyEnforceIf(b)
                            condition_vars.append(b)
                        except ValueError:
                            return f"Invalid number in token: {token} in row {i+1}"
                
                # At least one condition must be satisfied
                if condition_vars:
                    model.AddBoolOr(condition_vars)
    
    # Configure solver
    workers = 1
    if n > 100:
        workers = min(os.cpu_count(), 8)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    
    # Solve and return first solution
    status = solver.Solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        solution = [solver.Value(pos[i]) for i in range(n)]
        permutation = sorted(range(n), key=lambda x: solution[x])
        return [permutation]
    return []
