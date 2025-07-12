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
    center_idx = next(i for i,p in enumerate(parts) if '[' in p and ']' in p)
    # 3) Extract the bracket value and any trailing "-N"
    m = re.match(r'\[(\-?\d+)\](?:-(\d+))?$', parts[center_idx])
    center_val = int(m[1])
    # 4) Collect exclusion intervals (inclusive) as integer offsets from center
    excl: List[Tuple[int, int]] = []
    # 4a) If the bracket part has a "-N" suffix, treat that as [0..N]
    if m[2] is not None:
        b = int(m[2])
        excl.append((0, b))
    # 4b) Now handle every other segment
    for i, seg in enumerate(parts):
        if i == center_idx:
            continue
        # parse A-B (either A or B may be missing)
        ma = re.match(r'^(\d*)-(\d*)$', seg)
        if not ma:
            raise ValueError(f"cannot parse segment {seg!r}")
        a_str, b_str = ma.groups()
        # convert to ints or infinities
        if a_str == '':
            a = -inf
        else:
            a = int(a_str)
        if b_str == '':
            b = inf
        else:
            b = int(b_str)
        # now turn into offsets: if segment is before center, negate both
        if i < center_idx:
            a, b = -b, -a
        # ensure proper ordering
        start, end = min(a, b), max(a, b)
        excl.append((start, end))
    # 5) Merge & sort exclusions
    excl.sort()
    merged: List[Tuple[int,int]] = []
    for st, en in excl:
        if not merged or st > merged[-1][1] + 1:
            merged.append((st, en))
        else:
            # overlap or contiguous: extend
            merged[-1] = (merged[-1][0], max(merged[-1][1], en))
    # 6) Compute the complementary (allowed) intervals
    allowed: List[Tuple[float,float]] = []
    prev_end = -inf
    for st, en in merged:
        if prev_end <= st - 1:
            allowed.append((prev_end, st - 1))
        prev_end = en + 1
    # final tail
    allowed.append((prev_end, inf))
    # 7) Format as a string
    def fmt(x):
        if x == inf:
            return "float('inf')"
        if x == -inf:
            return "-float('inf')"
        return str(int(x))
    intervals_str = ", ".join(f"({fmt(a)}, {fmt(b)})" for a,b in allowed)
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

def go(strings, instructions, sorter):
    """
    Parses a list of instruction strings and applies appropriate constraint functions.

    Parameters:
    - strings: List[str], list of variable names.
    - instructions: List[List[str]], list of instruction lists corresponding to each string.
    """
    for idx, inst_list in enumerate(instructions):
        current = strings[idx]
        for inst in inst_list:
            inst = inst.strip()
            if not inst:
                continue

            # Forbidden constraint: [n] (a, b), ...
            m = re.match(r"^\[(\d+)\]\s*(.*)$", inst)
            if m:
                # Extract target index and interval string
                tgt_idx = int(m.group(1)) - 1
                target = strings[tgt_idx]
                intervals_part = m.group(2)

                # Parse intervals
                intervals = []
                for part in re.findall(r"\(([^)]+)\)", intervals_part):
                    lo_str, hi_str = map(str.strip, part.split(','))
                    lo = float(lo_str)
                    hi = math.inf if 'inf' in hi_str else float(hi_str)
                    intervals.append((lo, hi))

                sorter.add_forbidden_constraint(current, target, intervals)
                continue

            # Maximize distance constraint: as far as possible from n
            m2 = re.match(r"^as far as possible from\s+(\d+)$", inst)
            if m2:
                tgt_idx = int(m2.group(1)) - 1
                target = strings[tgt_idx]
                sorter.add_maximize_distance_constraint(current, target)
                continue

            # Unrecognized instruction
            raise ValueError(f"Unrecognized instruction: {inst}")
        
class ConstraintSorter:
    def __init__(self, elements: List[str]):
        self.elements = elements
        self.n = len(elements)
        self.forbidden_constraints = []  # (x, y, intervals) where x cannot be in intervals around y
        self.maximize_distance = []      # (x, y) where distance between x and y should be maximized
        
    def add_forbidden_constraint(self, x: str, y: str, intervals: List[Tuple[int, int]]):
        """
        Add a constraint that element x cannot be placed in specified intervals around element y.
        Intervals are relative positions: [-10,-6] means x cannot be 10 to 6 positions before y.
        Use float('inf') for 'end of list' in intervals.
        """
        self.forbidden_constraints.append((x, y, intervals))
    
    def add_maximize_distance_constraint(self, x: str, y: str):
        """
        Add a constraint that elements x and y should be as far apart as possible.
        """
        self.maximize_distance.append((x, y))
    
    def is_valid_placement(self, arrangement: List[str]) -> bool:
        """Check if an arrangement satisfies all forbidden constraints."""
        pos = {elem: i for i, elem in enumerate(arrangement)}
        
        for x, y, intervals in self.forbidden_constraints:
            if x not in pos or y not in pos:
                continue
                
            x_pos, y_pos = pos[x], pos[y]
            relative_pos = x_pos - y_pos
            
            # Check if x is in any forbidden interval around y
            for start, end in intervals:
                if end == float('inf'):
                    end = self.n - 1 - y_pos  # relative to end of list
                
                if start <= relative_pos <= end:
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
        
        # Create a mapping of elements involved in constraints
        constrained_elements = set()
        for x, y, _ in self.forbidden_constraints:
            constrained_elements.add(x)
            constrained_elements.add(y)
        
        # Place unconstrained elements first
        unconstrained = [elem for elem in self.elements if elem not in constrained_elements]
        positions = list(range(self.n))
        random.shuffle(positions)
        
        for i, elem in enumerate(unconstrained):
            if i < len(positions):
                arrangement[positions[i]] = elem
                remaining.remove(elem)
        
        # Place constrained elements
        for elem in remaining:
            placed = False
            for pos in range(self.n):
                if arrangement[pos] is None:
                    arrangement[pos] = elem
                    if self.is_valid_placement([e for e in arrangement if e is not None]):
                        placed = True
                        break
                    arrangement[pos] = None
            
            if not placed:
                # Force placement if necessary
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
            # Try random swaps
            i, j = random.sample(range(self.n), 2)
            
            # Create new arrangement with swap
            new_arrangement = current.copy()
            new_arrangement[i], new_arrangement[j] = new_arrangement[j], new_arrangement[i]
            
            # Check if new arrangement is valid
            if self.is_valid_placement(new_arrangement):
                new_score = self.calculate_distance_score(new_arrangement)
                
                # Accept if better score
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
            # Generate initial valid arrangement
            initial = self.generate_random_valid_arrangement()
            
            if initial is None:
                continue
            
            # Optimize using local search
            optimized = self.local_search_optimization(initial, max_iterations)
            
            # Check if this is the best solution so far
            if self.is_valid_placement(optimized):
                score = self.calculate_distance_score(optimized)
                if score > best_score:
                    best_arrangement = optimized
                    best_score = score
        
        return best_arrangement


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

def sorter(table, roles):
    instr_table = []
    for i, row in enumerate(table):
        instr_table.append([])
        for j, cell in enumerate(row):
            if roles[j] == 'dependencies':
                cell_list = cell.split(';')
                for instr in cell_list:
                    instr_table[i].append(get_intervals(instr.strip().lower()))
    alph = generate_unique_strings(len(roles))
    sorter = ConstraintSorter(alph)
    go(alph, instr_table, sorter)
    
    # Solve the problem
    print("Solving constraint-based sorting problem...")
    solution = sorter.solve(max_attempts=50, max_iterations=2000)
    
    if solution:
        print(f"Solution found: {solution}")
        print(f"Is valid: {sorter.is_valid_placement(solution)}")
        print(f"Distance score: {sorter.calculate_distance_score(solution)}")
        
        # Show positions for clarity
        print("\nPositions:")
        for i, elem in enumerate(solution):
            print(f"Position {i}: {elem}")
    else:
        print("No valid solution found!")