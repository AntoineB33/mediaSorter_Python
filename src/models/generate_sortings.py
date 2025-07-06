from ortools.sat.python import cp_model
import os
import re

def parse_constraint(entry, n):
    # Validate constraint format ends with - or _
    if not (entry.endswith('-') or entry.endswith('_')):
        return None, "Constraint must end with '-' or '_'"

    # Extract reference row
    ref_match = re.search(r'\[(\d+)\]', entry)
    if not ref_match:
        return None, "No reference found in constraint"
    
    try:
        ref_row = int(ref_match.group(1)) - 1
        if ref_row < 0 or ref_row >= n:
            return None, f"Reference row {ref_row+1} is out of range"
    except ValueError:
        return None, f"Invalid reference format: {ref_match.group(1)}"
    
    # Split into prefix and suffix
    prefix = entry[:ref_match.start()]
    suffix = entry[ref_match.end():]
    intervals = []
    
    # Helper function to parse tokens
    def parse_tokens(tokens, is_prefix):
        parsed = []
        for token in tokens:
            token = token.strip()
            if not token:
                continue
                
            if token == '-':
                # Entire negative/positive range
                parsed.append((None, -1) if is_prefix else (1, None))
            elif token.endswith('-'):
                # Open-ended range
                num_part = token[:-1]
                if not num_part:
                    parsed.append((None, -1) if is_prefix else (1, None))
                else:
                    try:
                        num = int(num_part)
                        parsed.append((None, -num) if is_prefix else (num, None))
                    except ValueError:
                        return None, f"Invalid number in open range: '{token}'"
            elif '-' in token:
                # Closed range
                parts = token.split('-')
                if len(parts) != 2:
                    return None, f"Invalid range format: '{token}'"
                try:
                    a = int(parts[0])
                    b = int(parts[1])
                    low, high = min(a, b), max(a, b)
                    parsed.append((-high, -low) if is_prefix else (low, high))
                except ValueError:
                    return None, f"Invalid numbers in range: '{token}'"
            else:
                # Single number
                try:
                    num = int(token)
                    parsed.append((-num, -num) if is_prefix else (num, num))
                except ValueError:
                    return None, f"Invalid number: '{token}'"
        return parsed, None
    
    # Process prefix tokens (negative offsets)
    prefix_tokens = prefix.split('_') if prefix else []
    prefix_intervals, error = parse_tokens(prefix_tokens, True)
    if error:
        return None, error
    intervals.extend(prefix_intervals)
    
    # Process suffix tokens (positive offsets)
    suffix_tokens = suffix.split('_') if suffix else []
    suffix_intervals, error = parse_tokens(suffix_tokens, False)
    if error:
        return None, error
    intervals.extend(suffix_intervals)
    
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
                    constraints.append((i, *constraint))
    
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
            elif a is None:
                model.Add(offset <= b).OnlyEnforceIf(bool_var)
            elif b is None:
                model.Add(offset >= a).OnlyEnforceIf(bool_var)
            bool_vars.append(bool_var)
        
        if bool_vars:
            model.AddBoolOr(bool_vars)
    
    # Configure solver
    solver = cp_model.CpSolver()
    workers = 1
    cpu_count = os.cpu_count() or 1
    
    if n > 100:
        workers = min(cpu_count, 4)
    if n > 300:
        workers = min(cpu_count, 6)
    if n > 500:
        workers = min(cpu_count, 8)
    if n > 1000:
        workers = min(cpu_count, 16)
    
    solver.parameters.num_search_workers = workers
    
    # Solve and return result
    status = solver.Solve(model)
    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        solution = [solver.Value(p) for p in positions]
        return [sorted(range(n), key=lambda i: solution[i])]
    return []