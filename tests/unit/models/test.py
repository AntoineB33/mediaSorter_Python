import re
import string

def process_table(table):
    row_labels = list(string.ascii_uppercase)
    n = len(table)
    labels = row_labels[:n]
    
    for i, row in enumerate(table):
        row_label = labels[i]
        for cell in row:
            if not isinstance(cell, str):
                continue
            
            # Forbidden constraint pattern: "-10_6-2_[55]_4-7_"
            forbidden_match = re.findall(r'(-?\d+)_(-?\d+)_?\[?(\d+)\]?', cell)
            if forbidden_match:
                ranges = []
                target_row = None
                parts = re.split(r'\[|\]', cell)
                if len(parts) >= 2:
                    target_row_idx = int(parts[1])
                    target_label = labels[target_row_idx]
                    ranges = re.findall(r'-?\d+_?-?\d*', parts[0] + parts[2])
                    parsed_ranges = []
                    for r in ranges:
                        nums = list(map(int, r.split('_')))
                        if len(nums) == 1:
                            parsed_ranges.append((nums[0], nums[0]))
                        elif len(nums) == 2:
                            low, high = nums
                            if r.endswith('_'):
                                high = float('inf')
                            parsed_ranges.append((low, high))
                    add_forbidden_constraint(row_label, target_label, parsed_ranges)

            # Distance maximization pattern: "as far as possible from 78"
            dist_match = re.search(r'as far as possible from (\d+)', cell, re.IGNORECASE)
            if dist_match:
                target_row_idx = int(dist_match.group(1))
                target_label = labels[target_row_idx]
                add_maximize_distance_constraint(row_label, target_label)

    return labels


def add_forbidden_constraint(from_label, to_label, ranges):
    print(f"Forbidden: {from_label} <-> {to_label} with ranges {ranges}")

def add_maximize_distance_constraint(from_label, to_label):
    print(f"Maximize distance: {from_label} <-> {to_label}")


table = [
    ["_[1]_1-8_", "as far as possible from 1"],
    ["nothing here", "irrelevant"],
    ["nothing here", "irrelevant"]
]

labels = process_table(table)
print(labels)
