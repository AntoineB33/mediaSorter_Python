import re
import random
from typing import List, Tuple, Dict, Set
from collections import defaultdict
import itertools
import string
import math
from math import inf
from typing import List, Tuple


def get_intervals(s: str) -> str:
    # 1) Split on '_' and drop empties
    parts = [p for p in s.split('_') if p]

    # 2) Find the bracketed center and its index
    center_idx = next(i for i, p in enumerate(parts) if '[' in p and ']' in p)

    # 3) Extract the bracket value and any trailing "-N" or "-" 
    m = re.match(r'\[(\-?\d+)\](?:-(\d*))?$', parts[center_idx])
    if not m:
        raise ValueError(f"cannot parse center segment {parts[center_idx]!r}")
    center_val = int(m.group(1))

    # 4) Collect exclusion intervals (inclusive) as integer offsets from center
    excl: List[Tuple[float, float]] = []

    # 4a) If the bracket part has a "-N" or "-" suffix, treat that as (1..N] or (1..∞)
    if m.group(2) is not None:
        if m.group(2) == '':
            b = inf
        else:
            b = int(m.group(2))
        # exclude offsets 1 through b
        excl.append((1, b))

    # 4b) Now handle every other segment
    for i, seg in enumerate(parts):
        if i == center_idx:
            continue
        ma = re.match(r'^(\d*)-(\d*)$', seg)
        if not ma:
            raise ValueError(f"cannot parse segment {seg!r}")
        a_str, b_str = ma.groups()
        a = -inf if a_str == '' else int(a_str)
        b = inf if b_str == '' else int(b_str)
        # convert to offsets relative to center
        if i < center_idx:
            a, b = -b, -a
        start, end = min(a, b), max(a, b)
        excl.append((start, end))

    # 5) Merge & sort exclusions
    excl.sort()
    merged: List[Tuple[float, float]] = []
    for st, en in excl:
        if not merged or st > merged[-1][1] + 1:
            merged.append((st, en))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], en))

    # 6) Compute complementary (allowed) intervals
    allowed: List[Tuple[float, float]] = []
    prev_end = -inf
    for st, en in merged:
        # gap before this exclusion
        if prev_end <= st - 1:
            allowed.append((prev_end, st - 1))
        prev_end = en + 1
    # final tail
    allowed.append((prev_end, inf))

    # 7) Drop any degenerate (inf, inf) tail
    allowed = [(a, b) for a, b in allowed if not (a == inf and b == inf)]

    # 8) Format
    def fmt(x):
        if x == inf:
            return "float('inf')"
        if x == -inf:
            return "-float('inf')"
        return str(int(x))

    intervals_str = ", ".join(f"({fmt(a)}, {fmt(b)})" for a, b in allowed)
    return f"[{center_val}] {intervals_str}"

def generate_unique_strings(n):
    charset = string.ascii_lowercase  # you can expand this (e.g. add digits or uppercase)
    result = []
    length = 1

    while len(result) < n:
        for combo in itertools.product(charset, repeat=length):
            result.append(''.join(combo))
            if len(result) == n:
                return result
        length += 1


def parse_intervals(intervals_part: str):
    """
    Given a string like "(-10, -6), (-2, 4), (7, float('inf')), (-float('inf'), 2)",
    returns a list of (lo, hi) tuples, with ±math.inf if 'inf' is present.
    """
    def to_num(s: str) -> float:
        s = s.strip()
        if 'inf' in s:
            return -math.inf if s.startswith('-') else math.inf
        return float(s)

    intervals = []
    i = 0
    n = len(intervals_part)
    while i < n:
        if intervals_part[i] == '(':
            depth = 1
            start = i + 1
            i += 1
            while i < n and depth > 0:
                if intervals_part[i] == '(':
                    depth += 1
                elif intervals_part[i] == ')':
                    depth -= 1
                i += 1
            chunk = intervals_part[start:i-1].strip()

            # Split on the top‑level comma
            depth2 = 0
            for j, c in enumerate(chunk):
                if c == '(':
                    depth2 += 1
                elif c == ')':
                    depth2 -= 1
                elif c == ',' and depth2 == 0:
                    lo_str, hi_str = chunk[:j], chunk[j+1:]
                    break
            else:
                raise ValueError(f"Malformed interval (no top-level comma): {chunk!r}")

            lo = to_num(lo_str)
            hi = to_num(hi_str)
            intervals.append((lo, hi))
        else:
            i += 1
    return intervals

def go(strings, instructions, sorter):
    for idx, inst_list in enumerate(instructions):
        current = strings[idx]
        for inst in inst_list:
            inst = inst.strip()
            if not inst:
                continue

            # Forbidden constraint
            m = re.match(r"^\[(\d+)\]\s*(.*)$", inst)
            if m:
                tgt_idx = int(m.group(1)) - 1
                target = strings[tgt_idx]
                intervals = parse_intervals(m.group(2))
                sorter.add_forbidden_constraint(current, target, intervals)
                continue

            # Maximize distance
            m2 = re.match(r"^as far as possible from\s+(\d+)$", inst)
            if m2:
                tgt_idx = int(m2.group(1)) - 1
                target = strings[tgt_idx]
                sorter.add_maximize_distance_constraint(current, target)
                continue

            raise ValueError(f"Unrecognized instruction: {inst}")

class ConstraintSorter:
    def __init__(self, elements: List[str]):
        self.elements = elements
        self.n = len(elements)
        self.forbidden_constraints = []      # (x, y, intervals) where x cannot be in intervals around y
        # New constraint type: (x, y_list, intervals)
        # x's position relative to *at least one* y in y_list must NOT be in the forbidden intervals.
        self.required_disjunctive_constraints = []
        self.maximize_distance = []          # (x, y) where distance between x and y should be maximized

    def add_forbidden_constraint(self, x: str, y: str, intervals: List[Tuple[int, int]]):
        """
        Add a constraint that element x cannot be placed in specified intervals around element y.
        Intervals are relative positions: [-10,-6] means x cannot be 10 to 6 positions before y.
        Use float('inf') for 'end of list' in intervals.
        """
        self.forbidden_constraints.append((x, y, intervals))

    def add_forbidden_constraint_any_y(self, x: str, y_list: List[str], intervals: List[Tuple[int, int]]):
        """
        Adds a constraint that x's relative position to AT LEAST ONE element in y_list
        must fall OUTSIDE the specified forbidden intervals.

        For example:
        add_forbidden_constraint_any_y('E', ['F', 'G', 'H'], [(-float('inf'), 0), (2, float('inf'))])
        This defines the forbidden relative positions as (<= 0) or (>= 2).
        Therefore, the only allowed relative position is 1.
        The constraint means that (pos(E) - pos(y)) must be 1 for at least one y in ['F', 'G', 'H'].
        In other words, E must immediately follow F, or G, or H.
        """
        self.required_disjunctive_constraints.append((x, y_list, intervals))

    def add_maximize_distance_constraint(self, x: str, y: str):
        """
        Add a constraint that elements x and y should be as far apart as possible.
        """
        self.maximize_distance.append((x, y))

    def is_valid_placement(self, arrangement: List[str]) -> bool:
        """Check if an arrangement satisfies all constraints."""
        pos = {elem: i for i, elem in enumerate(arrangement) if elem is not None}

        # 1. Check standard forbidden constraints
        for x, y, intervals in self.forbidden_constraints:
            if x not in pos or y not in pos:
                continue

            x_pos, y_pos = pos[x], pos[y]
            relative_pos = x_pos - y_pos

            for start, end in intervals:
                _start, _end = start, end
                if _end == float('inf'):
                    _end = self.n  # A safe upper bound
                if _start == -float('inf'):
                    _start = -self.n # A safe lower bound

                if _start <= relative_pos <= _end:
                    return False  # Violation

        # 2. Check the "required disjunctive" constraints
        for x, y_list, intervals in self.required_disjunctive_constraints:
            if x not in pos:
                continue

            is_satisfied_for_x = False
            # Check if any y in the list satisfies the condition for x
            for y in y_list:
                if y not in pos:
                    continue

                x_pos, y_pos = pos[x], pos[y]
                relative_pos = x_pos - y_pos

                is_in_forbidden_zone = False
                for start, end in intervals:
                    _start, _end = start, end
                    if _end == float('inf'):
                        _end = self.n
                    if _start == -float('inf'):
                        _start = -self.n

                    if _start <= relative_pos <= _end:
                        is_in_forbidden_zone = True
                        break  # It's in a forbidden interval, this y is not valid

                if not is_in_forbidden_zone:
                    # Found a 'y' for which 'x' is in an allowed position.
                    is_satisfied_for_x = True
                    break  # This disjunctive constraint is satisfied, move to the next one

            # If x is placed and we couldn't find any y in y_list that satisfies
            # the constraint, the arrangement is invalid.
            if not is_satisfied_for_x and any(y in pos for y in y_list):
                return False

        return True

    def calculate_distance_score(self, arrangement: List[str]) -> float:
        """Calculate score based on distance maximization constraints (higher is better)."""
        pos = {elem: i for i, elem in enumerate(arrangement)}
        total_distance = 0

        for x, y in self.maximize_distance:
            if x in pos and y in pos:
                distance = abs(pos[x] - pos[y])
                total_distance += distance

        return total_distance

    def generate_random_valid_arrangement(self, max_attempts: int = 1000) -> List[str]:
        """Generate a random valid arrangement that satisfies all forbidden constraints."""
        for _ in range(max_attempts):
            arrangement = self.elements.copy()
            random.shuffle(arrangement)

            if self.is_valid_placement(arrangement):
                return arrangement

        # If we can't find a valid random arrangement, try a more systematic approach
        return self.greedy_placement()

    def greedy_placement(self) -> List[str]:
        """Try to place elements greedily to satisfy constraints."""
        arrangement = [None] * self.n
        remaining = set(self.elements)

        constrained_elements = set()
        for x, y, _ in self.forbidden_constraints:
            constrained_elements.add(x)
            constrained_elements.add(y)
        for x, y_list, _ in self.required_disjunctive_constraints:
            constrained_elements.add(x)
            constrained_elements.update(y_list)

        unconstrained = [elem for elem in self.elements if elem not in constrained_elements]
        positions = list(range(self.n))
        random.shuffle(positions)

        for i, elem in enumerate(unconstrained):
            if i < len(positions):
                arrangement[positions[i]] = elem
                remaining.remove(elem)

        for elem in list(remaining):
            placed = False
            shuffled_positions = list(range(self.n))
            random.shuffle(shuffled_positions)
            for pos in shuffled_positions:
                if arrangement[pos] is None:
                    arrangement[pos] = elem
                    # Check if the partial arrangement is valid
                    if self.is_valid_placement(arrangement):
                        placed = True
                        break
                    arrangement[pos] = None # Backtrack

            if not placed:
                 # Force placement if no valid spot is found (may result in invalid solution)
                 # A more robust implementation might raise an error or return None here.
                for pos in range(self.n):
                    if arrangement[pos] is None:
                        arrangement[pos] = elem
                        break
        return arrangement

    def local_search_optimization(self, initial_arrangement: List[str], max_iterations: int = 1000) -> List[str]:
        """Improve arrangement using local search while maintaining constraint satisfaction."""
        current = initial_arrangement.copy()
        current_score = self.calculate_distance_score(current)

        for _ in range(max_iterations):
            i, j = random.sample(range(self.n), 2)
            new_arrangement = current.copy()
            new_arrangement[i], new_arrangement[j] = new_arrangement[j], new_arrangement[i]

            if self.is_valid_placement(new_arrangement):
                new_score = self.calculate_distance_score(new_arrangement)
                if new_score > current_score:
                    current = new_arrangement
                    current_score = new_score

        return current

    def solve(self, max_attempts: int = 10, max_iterations: int = 1000) -> List[str]:
        """
        Solve the constraint satisfaction problem.
        Returns the best arrangement found.
        """
        best_arrangement = None
        best_score = -1

        for attempt in range(max_attempts):
            initial = self.generate_random_valid_arrangement()
            if initial is None or not self.is_valid_placement(initial):
                continue

            optimized = self.local_search_optimization(initial, max_iterations)

            score = self.calculate_distance_score(optimized)
            if score > best_score:
                # Final check to ensure the best one is always valid
                if self.is_valid_placement(optimized):
                    best_arrangement = optimized
                    best_score = score

        return best_arrangement

def order_table(res, table, roles):
    res.insert(0, -1)
    old_to_new = {old_index+1: new_index+1 for new_index, old_index in enumerate(res)}
    new_table = []
    for old_index in res:
        original_row = table[old_index+1]
        new_row = []
        for j, cell in enumerate(original_row):
            if roles[j] == 'dependencies':
                if isinstance(cell, str):
                    updated_cell = re.sub(r'\d+', lambda m: str(old_to_new[int(m.group(0))]), cell)
                    new_row.append(updated_cell)
                else:
                    new_row.append(cell)
            else:
                new_row.append(cell)
        new_table.append(new_row)
    return new_table

def sorter(table, roles):
    instr_table = []
    dep_pattern = [cell.split('.') for cell in table[0]]
    attributes = {}
    for i, row in enumerate(table[1:]):
        for j, cell in enumerate(row):
            if roles[j] == 'attributes':
                cell_list = cell.split(';')
                for cat in cell_list:
                    if cat not in attributes:
                        attributes[cat] = []
                    if i not in attributes[cat]:
                        attributes[cat].append(i+1)
                    else:
                        print(f"Error in row {i+1}, column {j+1}: category {cat!r} already exists for this row")
                        return f"Error in row {i+1}, column {j+1}: category {cat!r} already exists for this row"
    for i, row in enumerate(table[1:]):
        instr_table.append([])
        for j, cell in enumerate(row):
            if roles[j] == 'dependencies':
                cell_list = cell.split(';')
                for instr in cell_list:
                    if instr:
                        instr_split = instr.split('.')
                        if len(instr_split) != len(dep_pattern[j])-1:
                            print(f"Error in row {i+1}, column {j+1}: {instr!r} does not match dependencies pattern {dep_pattern[j]!r}")
                            return f"Error in row {i+1}, column {j+1}: {instr!r} does not match dependencies pattern {dep_pattern[j]!r}"
                        if dep_pattern[j]:
                            instr = dep_pattern[j][0] + ''.join([instr_split[i]+dep_pattern[j][i+1] for i in range(len(instr_split))])
                        match = re.match(r'^as far as possible from (\((\d+)\)|(\d+))$', instr)
                        if match:
                            if match.group(2):
                                number = int(match.group(2))
                                for r in attributes.get(number, []):
                                    instr_table[i].append(f"as far as possible from {r}")
                            else:
                                instr_table[i].append(instr)
                        else:
                            try:
                                instr = get_intervals(instr)
                                # Pattern to match strings like "[(55)] ..." and capture the number and rest
                                pattern = r'\[\((\d+)\)\](.*)'

                                match = re.match(pattern, instr)
                                if match:
                                    rest_of_string = match.group(2)
                                    for r in attributes.get(number, []):
                                        instr_table[i].append(f"[{r}]{rest_of_string}")
                                else:
                                    instr_table[i].append(instr)
                            except ValueError as e:
                                print(f"Error parsing instruction '{instr}' in row {i}, column {j}: {e}")
    not_finished = len(table[1:])
    finished = [False for _ in range(not_finished)]
    while not_finished:
        for i, row in table[1:]:
            if finished[i]:
                continue
            has_unresolved = False
            for j, cell in enumerate(row):
                if roles[j] == 'pointers':
                    instr = cell.split(';')
                    for instr_item in instr:
                        try:
                            if not finished[int(instr_item)-1]:
                                has_unresolved = True
                                break
                        except ValueError:
                            print(f"Error in row {i+1}, column {j+1}: invalid pointer {instr_item!r}")
                            return f"Error in row {i+1}, column {j+1}: invalid pointer {instr_item!r}"
                    if has_unresolved:
                        break
            if not has_unresolved:
                for j, cell in enumerate(row):
                    if roles[j] == 'pointers':
                        instr = cell.split(';')
                        for pointed_row in instr:
                            instr_table[i] += instr_table[int(pointed_row)-1]
                            path = table[int(pointed_row)][roles.index('path')]
                            if path:
                                if row[roles.index('path')]:
                                    print(f"Warning: row {i+1} has a path {row[roles.index('path')]} but also points to row {int(pointed_row)} with path {path}.")
                                    return f"Warning: row {i+1} has a path {row[roles.index('path')]} but also points to row {int(pointed_row)} with path {path}."
                                row[roles.index('path')] = path
                finished[i] = True
                not_finished -= 1
    new_indexes = []
    for i, row in enumerate(table[1:]):
        
    alph = generate_unique_strings(len(table)-1)
    sorter = ConstraintSorter(alph)
    go(alph, instr_table, sorter)
    
    # Solve the problem
    print("Solving constraint-based sorting problem...")
    solution = sorter.solve(max_attempts=50, max_iterations=2000)
    
    if not solution:
        print("No valid solution found!")
        return "No valid solution found!"
    if type(solution) is string:
        return solution
    print(f"Solution found: {solution}")
    print(f"Is valid: {sorter.is_valid_placement(solution)}")
    print(f"Distance score: {sorter.calculate_distance_score(solution)}")
    
    # Show positions for clarity
    print("\nPositions:")
    for i, elem in enumerate(solution):
        print(f"Position {i}: {elem}")
    
    res = [alph.index(elem) for elem in solution]
    new_table = order_table(res, table)
    new_table.insert(0, table[0])  # Add header back
    return new_table

if __name__ == "__main__":
    #take from clipboard
    import pyperclip
    clipboard_content = pyperclip.paste()
    table = [line.split('\t') for line in clipboard_content.split('\n')]
    roles = table[0]
    result = sorter(table[1:], roles)
    new_clipboard_content = '\n'.join(['\t'.join(row) for row in result])
    pyperclip.copy(new_clipboard_content)