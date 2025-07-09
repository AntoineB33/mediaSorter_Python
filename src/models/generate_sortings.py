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
    
def find_valid_sortings0(table):
    import random
    n = len(table)

    # returns table in a random order
    return random.sample(range(n), n)

import itertools

def find_valid_sortings(table):
    n = len(table)
    constraints = {}
    far_constraints = {}
    
    for i in range(n):
        if table[i]:
            for item in table[i]:
                if isinstance(item, str):
                    if '_' in item or '[' in item or '-' in item:
                        segments = [s.strip() for s in item.split('_') if s.strip() != '']
                        ref_row = None
                        intervals = []
                        for seg in segments:
                            if '[' in seg and ']' in seg:
                                start_idx = seg.index('[')
                                end_idx = seg.index(']')
                                ref_str = seg[start_idx+1:end_idx]
                                try:
                                    ref_row = int(ref_str)
                                except:
                                    pass
                                new_seg = seg[:start_idx] + seg[end_idx+1:]
                                if new_seg != '':
                                    parts = new_seg.split('-', 1)
                                    a_str = parts[0] if len(parts) > 0 else ''
                                    b_str = parts[1] if len(parts) > 1 else ''
                                    a_val = -10**9 if a_str == '' else int(a_str)
                                    b_val = 10**9 if b_str == '' else int(b_str)
                                    low = min(a_val, b_val)
                                    high = max(a_val, b_val)
                                    intervals.append((low, high))
                            else:
                                parts = seg.split('-', 1)
                                a_str = parts[0] if len(parts) > 0 else ''
                                b_str = parts[1] if len(parts) > 1 else ''
                                a_val = -10**9 if a_str == '' else int(a_str)
                                b_val = 10**9 if b_str == '' else int(b_str)
                                low = min(a_val, b_val)
                                high = max(a_val, b_val)
                                intervals.append((low, high))
                        if ref_row is not None:
                            constraints[i] = (ref_row, intervals)
                    elif "as far as possible from" in item:
                        parts = item.split()
                        if parts:
                            last_word = parts[-1]
                            try:
                                ref_index = int(last_word)
                                far_constraints[i] = ref_index
                            except:
                                pass
    
    all_rows = list(range(n))
    valid_perms = []
    
    for perm in itertools.permutations(all_rows):
        pos_dict = {row_idx: idx for idx, row_idx in enumerate(perm)}
        valid = True
        for i, (ref_row, intervals) in constraints.items():
            if i not in pos_dict or ref_row not in pos_dict:
                valid = False
                break
            d = abs(pos_dict[i] - pos_dict[ref_row])
            found_interval = False
            for (low, high) in intervals:
                if low <= d <= high:
                    found_interval = True
                    break
            if not found_interval:
                valid = False
                break
        if valid:
            valid_perms.append(perm)
    
    if not valid_perms:
        return "No valid sorting found."
    
    if not far_constraints:
        return list(valid_perms[0])
    
    best_perm = None
    best_obj = -1
    for perm in valid_perms:
        pos_dict = {row_idx: idx for idx, row_idx in enumerate(perm)}
        obj = 0
        for i, ref_row in far_constraints.items():
            if i in pos_dict and ref_row in pos_dict:
                obj += abs(pos_dict[i] - pos_dict[ref_row])
        if obj > best_obj:
            best_obj = obj
            best_perm = perm
    
    return list(best_perm)

def find_valid_sortings2(table, roles):
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