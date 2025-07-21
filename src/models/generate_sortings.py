import re
import random
from typing import List, Tuple, Dict, Set
from collections import defaultdict
import itertools
import string
import math
from math import inf
from typing import List, Tuple

PATTERN_DISTANCE = r'^(?P<prefix>as far as possible from )(?P<any>any)?((?P<number>\d+)|(?P<name>.+))(?P<suffix>)$'
PATTERN_AREAS = r'^(?P<prefix>.*\|)(?P<any>any)?((?P<number>\d+)|(?P<name>.+))(?P<suffix>\|.*)$'

def get_intervals(interval_str):
    # First, parse the positions of intervals
    intervals = [[], []]
    neg_pos = re.split(r'\[(\((\d+)\)|(\d+))\]', interval_str)
    positive = 0
    for neg_pos_part in [neg_pos[0], neg_pos[4]]:
        parts = re.split(r'_', neg_pos_part)
        for part in parts:
            if not part:
                intervals[positive].append((None, None))
            elif ":" in part:
                start, end = part.split(':')
                try:
                    start = int(start)
                except:
                    start = float('inf')
                try:
                    end = int(end)
                except:
                    end = float('inf')
                if not positive:
                    start = -start
                    end = -end
                intervals[positive].append((start, end))
            else:
                intervals[positive].append((int(part), int(part)))
        positive = 1

    # Now calculate underscore intervals
    result = []
    positive = 0
    for neg_pos_part in intervals:
        for i in range(len(neg_pos_part) - 1):
            end_of_current = neg_pos_part[i][1]
            start_of_next = neg_pos_part[i+1][0]
            if end_of_current is None:
                if not positive:
                    end_of_current = -float('inf')
                elif result and result[-1][1] == -1:
                    end_of_current = result[-1][0] - 1
                    del result[-1]
                else:
                    end_of_current = 0
            if start_of_next is None:
                if not positive:
                    start_of_next = 0
                else:
                    start_of_next = float('inf')
            if start_of_next - end_of_current <= 1:
                raise ValueError("Invalid interval: overlapping or adjacent intervals found.")
            result.append((end_of_current + 1, start_of_next - 1))
        positive = 1
    
    return "[" + neg_pos[1] + "] " + ', '.join(f"({start}, {end})" for start, end in result)

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
    new_pos = [0] * len(table)
    for i, old_index in enumerate(res):
        new_pos[old_index+1] = i+1
    new_table = [table[0]]
    for original_row in table[1:]:
        new_row = []
        for j, cell in enumerate(original_row):
            if roles[j] == 'dependencies':
                updated_cell = cell.split(';')
                for d, instr in enumerate(list(updated_cell)):
                        match = re.match(PATTERN_DISTANCE, instr)
                        if not match:
                            match = re.match(PATTERN_AREAS, instr)
                        if match.group("number"):
                            number = int(match.group("number"))
                            updated_cell[d].append(f"{match.group('prefix')}{"any" if match.group('any') else ''}{new_pos[number]}{match.group('suffix')}")
                new_row.append(updated_cell)
            else:
                new_row.append(cell)
        new_table.append(new_row)
    return new_table

def sorter(table, roles, errors, warnings):
    path_index = roles.index('path') if 'path' in roles else -1
    if path_index != -1:
        for i, row in enumerate(table[1:]):
            cell = row[path_index]
            if cell:
                if not cell.strip():
                    warnings.append(f"Warning in row {i+1}, column {path_index+1}: only whitespace in cell")
                if not re.match(r'^(https?://|file://)', cell):
                    warnings.append(f"Warning in row {i+1}, column {path_index+1}: {cell!r} is not a valid URL or local path")
    pointed_by = [[] for _ in range(len(table))]
    point_to = [[] for _ in range(len(table))]
    for i, row in enumerate(table[1:], start=1):
        for j, cell in enumerate(row):
            if roles[j] == 'pointers':
                if cell:
                    cell_list = cell.split(';')
                    for instr in cell_list:
                        try:
                            k = int(instr)
                            if k < 1 or k > len(table)-1:
                                errors.append(f"Error in row {i}, column {j+1}: {instr!r} points to an invalid row {k}")
                                return table
                            else:
                                pointed_by[k].append(i)
                                point_to[i].append(k)
                        except ValueError:
                            errors.append(f"Error in row {i}, column {j+1}: {instr!r} is not a valid pointer")
                            return table
    # find a cycle
    def dfs(node, visited, stack):
        visited.add(node)
        stack.add(node)
        for neighbor in point_to[node]:
            if neighbor not in visited:
                if dfs(neighbor, visited, stack):
                    return True
            elif neighbor in stack:
                return True
        stack.remove(node)
        return False
    visited = set()
    stack = set()
    for i in range(1, len(table)):
        if i not in visited:
            if dfs(i, visited, stack):
                print(f"Cycle found starting at row {i}")
                return table
    attributes = {}
    attributes_table = [[] for _ in range(len(table))]
    names = [[] for _ in range(len(table))]
    for i, row in enumerate(table[1:], start=1):
        for j, cell in enumerate(row):
            if roles[j] == 'attributes':
                cell_list = cell.split(';')
                for cat in cell_list:
                    if cat not in attributes:
                        attributes[cat] = []
                    if i not in attributes[cat]:
                        attributes[cat].append(i)
                        attributes_table[i].append(cat)
                    else:
                        warnings.append(f"Redundant attribute {cat!r} in row {i}, column {j+1}")
            elif roles[j] == 'names':
                cell_list = cell.split(';')
                for name in cell_list:
                    if name not in names[i]:
                        names[i].append(name)
                    else:
                        warnings.append(f"Redundant name {name!r} in row {i}, column {j+1}")
    pointed_givers = [dict() for _ in range(len(table))]
    pointed_givers_path = [0 for _ in range(len(table))]
    pointed_by_all = [list() for i in range(len(table))]
    point_to_all = [list() for i in range(len(table))]
    for i, row in enumerate(pointed_by_all[1:], start=1):
        to_check = list(pointed_by[i])
        while to_check:
            current = to_check.pop()
            if current not in row:
                row.append(current)
                point_to_all[current].append(i)
                for cat in attributes_table[i]:
                    if cat not in attributes_table[current]:
                        attributes_table[current].append(cat)
                        attributes[cat].append(current)
                        pointed_givers[current][cat] = i
                    elif cat not in pointed_givers[current]:
                        warnings.append(f"Redundant attribute {cat!r} in row {current} already given by row {i}")
                if path_index != -1 and table[i][path_index]:
                    if table[current][path_index] and not pointed_givers_path[current]:
                        warnings.append(f"Warning in row {current}, column {path_index+1}: path already given by row {i}")
                    table[current][path_index] = table[i][path_index]
                    pointed_givers_path[current] = i
            to_check.extend(pointed_by[current])
    valid_row_indexes = []
    new_indexes = list(range(len(table)))
    to_old_indexes = []
    staying = [False]
    cat_rows = []
    new_index = 1
    for i, row in enumerate(table[1:], start=1):
        staying.append(False)
        if path_index != -1 and row[path_index]:
            valid_row_indexes.append(i)
            staying[i] = True
            new_indexes[i] = new_index
            new_index += 1
            to_old_indexes.append(i)
        else:
            cat_rows.append(i)
    for cat in attributes:
        attributes[cat] = list(filter(lambda x: staying[x], attributes[cat]))
    for row in pointed_by_all:
        row[:] = list(filter(lambda x: staying[x], row))
    instr_table = [[] for _ in range(len(table))]
    dep_pattern = [cell.split('.') for cell in table[0]]
    for i, row in enumerate(table[1:], start=1):
        if not staying[i] and not pointed_by[i]:
            continue
        for j, cell in enumerate(row):
            if roles[j] == 'dependencies' and cell:
                cell_list = cell.split(';')
                for instr in cell_list:
                    if instr:
                        instr_split = instr.split('.')
                        if len(instr_split) != len(dep_pattern[j])-1:
                            errors.append(f"Error in row {i+1}, column {j+1}: {instr!r} does not match dependencies pattern {dep_pattern[j]!r}")
                            return table
                        if dep_pattern[j]:
                            instr = dep_pattern[j][0] + ''.join([instr_split[i]+dep_pattern[j][i+1] for i in range(len(instr_split))])
                        match = re.match(PATTERN_DISTANCE, instr)
                        if not match:
                            match = re.match(PATTERN_AREAS, instr)
                            if not match:
                                errors.append(f"Error in row {i+1}, column {j+1}: {instr!r} does not match expected format")
                                return table
                        any_str = "any" if match.group("any") else ""
                        numbers = []
                        if match.group("number"):
                            number = int(match.group("number"))
                            if number == 0 or number > len(table):
                                errors.append(f"Error in row {i}, column {j+1}: invalid number.")
                                return table
                            if staying[number]:
                                numbers.append(number)
                            for pointer in pointed_by_all[number]:
                                numbers.append(pointer)
                        elif name := match.group("name"):
                            if name in attributes:
                                for r in attributes[name]:
                                    numbers.append(r)
                            else:
                                for ii, rrow in enumerate(names[1:], start=1):
                                    if name in rrow:
                                        number = ii
                                        if staying[number]:
                                            numbers.append(number)
                                        for pointer in pointed_by_all[number]:
                                            numbers.append(pointer)
                                        break
                                else:
                                    errors.append(f"Error in row {i+1}, column {j+1}: attribute {name!r} does not exist")
                                    return table
                        else:
                            errors.append(f"Error in row {i+1}, column {j+1}: {instr!r} does not match expected format")
                            return table
                        for number in numbers:
                            instr_table[i].append(f"{match.group('prefix')}{any_str}{number}{match.group('suffix')}")
    for i in valid_row_indexes:
        for p in pointed_by_all[i]:
            instr_table[p] = list(set(instr_table[p] + instr_table[i]))
    instr_table_int = []
    for i in valid_row_indexes:
        instr_table_int.append(instr_table[i-1])
    alph = generate_unique_strings(len(valid_row_indexes))
    sorter = ConstraintSorter(alph)
    go(alph, instr_table_int, sorter)
    
    # Solve the problem
    print("Solving constraint-based sorting problem...")
    solution = sorter.solve(max_attempts=50, max_iterations=2000)
    
    if not solution:
        errors.append("No valid solution found!")
        return table
    elif type(solution) is string:
        errors.append(f"Error when sorting: {solution!r}")
        return table
    print(f"Solution found: {solution}")
    print(f"Is valid: {sorter.is_valid_placement(solution)}")
    print(f"Distance score: {sorter.calculate_distance_score(solution)}")
    
    # Show positions for clarity
    print("\nPositions:")
    for i, elem in enumerate(solution):
        print(f"Position {i}: {elem}")
    
    res = [to_old_indexes[alph.index(elem)]-1 for elem in solution]
    i = 0
    while i < len(res):
        d = 0
        while d < len(cat_rows):
            e = cat_rows[d]
            if e in point_to_all[res[i]+1]:
                res.insert(i, e-1)
                i += 1
                del cat_rows[d]
            else:
                d += 1
        i += 1
    new_table = order_table(res, table, roles)
    return new_table


if __name__ == "__main__":
    #take from clipboard
    import pyperclip
    clipboard_content = pyperclip.paste()
    table = [line.split('\t') for line in clipboard_content.split('\n')]
    for row in table:
        row[-1] = row[-1].strip()
    roles = table[0]
    warnings = []
    errors = []
    result = sorter(table[1:], roles, errors, warnings)
    result.insert(0, roles)
    if errors:
        print("Errors found:")
        for error in errors:
            print(f"- {error}")
    if warnings:
        print("Warnings found:")
        for warning in warnings:
            print(f"- {warning}")
    new_clipboard_content = '\n'.join(['\t'.join(row) for row in result])
    pyperclip.copy(new_clipboard_content)
    input("Sorted table copied to clipboard. Press Enter to exit.")