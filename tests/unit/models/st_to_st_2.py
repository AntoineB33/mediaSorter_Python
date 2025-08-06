import re
from typing import List, Tuple

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

# Examples
print(get_intervals(":2_[45]_8:"))
print(get_intervals(":[2]_4:5_7:"))
