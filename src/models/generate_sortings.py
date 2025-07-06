from ortools.sat.python import cp_model
import os
import re

def parse_constraint(entry, n):
    ref_matches = re.findall(r'\[(\d+)\]', entry)
    if not ref_matches:
        return None, f"Invalid entry: no reference found in '{entry}'"
    if len(ref_matches) > 1:
        return None, f"Invalid entry: multiple references in '{entry}'"
    
    try:
        ref_row = int(ref_matches[0]) - 1
        if ref_row < 0 or ref_row >= n:
            return None, f"Invalid reference row: {ref_matches[0]}"
    except ValueError:
        return None, f"Invalid reference format: {ref_matches[0]}"
    
    match = re.search(r'\[(\d+)\]', entry)
    prefix = entry[:match.start()]
    suffix = entry[match.end():]
    intervals = []
    
    # Parse prefix (negative offsets)
    tokens = prefix.split('_')
    for token in tokens:
        token = token.strip()
        if not token: 
            continue
        if token == '-':
            intervals.append((None, -1))  # All negative offsets
        else:
            if '-' in token:
                parts = token.split('-')
                if len(parts) != 2:
                    return None, f"Invalid range format: {token}"
                try:
                    a = int(parts[0])
                    b = int(parts[1])
                    low = min(a, b)
                    high = max(a, b)
                    intervals.append((-high, -low))  # Negative range
                except ValueError:
                    return None, f"Invalid numbers in range: {token}"
            else:
                try:
                    num = int(token)
                    intervals.append((-num, -num))  # Single negative offset
                except ValueError:
                    return None, f"Invalid number: {token}"
    
    # Parse suffix (positive offsets)
    tokens = suffix.split('_')
    for token in tokens:
        token = token.strip()
        if not token: 
            continue
        if token == '-':
            intervals.append((1, None))  # All positive offsets
        elif token.endswith('-'):
            num_part = token[:-1].strip()
            if not num_part:
                intervals.append((1, None))  # All positive
            else:
                try:
                    num = int(num_part)
                    intervals.append((num, None))  # From num onward
                except ValueError:
                    return None, f"Invalid number in trailing dash: {token}"
        elif '-' in token:
            parts = token.split('-')
            if len(parts) != 2:
                return None, f"Invalid range format: {token}"
            try:
                a = int(parts[0])
                b = int(parts[1])
                low = min(a, b)
                high = max(a, b)
                intervals.append((low, high))  # Positive range
            except ValueError:
                return None, f"Invalid numbers in range: {token}"
        else:
            try:
                num = int(token)
                intervals.append((num, num))  # Single positive offset
            except ValueError:
                return None, f"Invalid number: {token}"
    
    return (ref_row, intervals), None

def find_valid_sortings(table, roles):
    n = len(table)
    constraints = []
    
    # Parse all constraints
    for i in range(n):
        for c, cell in enumerate(table[i]):
            if roles[c] != 'dependencies':
                continue
            entries = cell.split(';')
            for entry in entries:
                entry = entry.strip()
                if not entry:
                    continue
                constraint, error = parse_constraint(entry, n)
                if error:
                    return f"{error} in row {i+1}"
                if constraint:
                    constraints.append((i, constraint[0], constraint[1]))
    
    # Create CP model
    model = cp_model.CpModel()
    positions = [model.NewIntVar(0, n-1, f'pos_{i}') for i in range(n)]
    model.AddAllDifferent(positions)
    
    # Add constraints
    for idx, (i, ref, intervals) in enumerate(constraints):
        offset = positions[i] - positions[ref]
        bool_vars = []
        
        for j, (a, b) in enumerate(intervals):
            bool_var = model.NewBoolVar(f'c_{idx}_{j}')
            if a is not None and b is not None:
                model.Add(offset >= a).OnlyEnforceIf(bool_var)
                model.Add(offset <= b).OnlyEnforceIf(bool_var)
            elif a is None and b is not None:
                model.Add(offset <= b).OnlyEnforceIf(bool_var)
            elif a is not None and b is None:
                model.Add(offset >= a).OnlyEnforceIf(bool_var)
            else:  # (None, None)
                model.Add(bool_var == 1)
            bool_vars.append(bool_var)
        
        model.AddBoolOr(bool_vars)
    
    # Configure solver
    solver = cp_model.CpSolver()
    workers = 1
    if n > 100:
        workers = min(os.cpu_count() or 1, 4)
    if n > 300:
        workers = min(os.cpu_count() or 1, 6)
    if n > 500:
        workers = min(os.cpu_count() or 1, 8)
    if n > 1000:
        workers = min(os.cpu_count() or 1, 16)
    solver.parameters.num_search_workers = workers
    
    # Solve and return result
    status = solver.Solve(model)
    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        solution = [solver.Value(p) for p in positions]
        return [sorted(range(n), key=lambda i: solution[i])]
    return []