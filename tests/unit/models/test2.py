import re
import math

def add_forbidden_constraint(current, target, intervals):
    # Placeholder implementation
    print(f"add_forbidden_constraint({current!r}, {target!r}, {intervals})")

def add_maximize_distance_constraint(current, target):
    # Placeholder implementation
    print(f"add_maximize_distance_constraint({current!r}, {target!r})")

def go(strings, instructions):
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

                add_forbidden_constraint(current, target, intervals)
                continue

            # Maximize distance constraint: as far as possible from n
            m2 = re.match(r"^as far as possible from\s+(\d+)$", inst)
            if m2:
                tgt_idx = int(m2.group(1)) - 1
                target = strings[tgt_idx]
                add_maximize_distance_constraint(current, target)
                continue

            # Unrecognized instruction
            raise ValueError(f"Unrecognized instruction: {inst}")

# Example usage
test_strings = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
test_instructions = [
    ["[3] (-10, -6), (-2, 4), (7, float('inf'))", "[2] (-3, 2)"],
    ["[2] (-float('inf'), 2)"],
    ["as far as possible from 1"],
    ["as far as possible from 2"],
    [""],
    ["[3] (-5, 0)"],
    ["as far as possible from 4"]
]

go(test_strings, test_instructions)  # Demonstrate parsing
