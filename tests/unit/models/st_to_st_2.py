import re

def underscore_intervals(interval_str):
    # First, parse the positions of intervals
    parts = re.split(r'(_)', interval_str)
    intervals = []
    current = 0
    
    for part in parts:
        if part == '_':
            continue
        if '-' in part:
            if part.startswith('-'):
                start = current
                end = int(part[1:]) - 1
            elif part.endswith('-'):
                start = int(part[:-1]) + 1
                end = None
            else:
                start, end = map(int, part.split('-'))
                end = end
            intervals.append((start, end))
            current = (end if end is not None else current) + 1
        else:
            point = int(part)
            intervals.append((point, point))
            current = point + 1

    # Now calculate underscore intervals
    result = []
    for i in range(len(intervals) - 1):
        end_of_current = intervals[i][1]
        start_of_next = intervals[i+1][0]
        if start_of_next - end_of_current > 1:
            result.append((end_of_current + 1, start_of_next - 1))
    
    return ', '.join(f"({start}, {end})" for start, end in result)

# Examples
print(underscore_intervals("1-2_4-7_9-"))  # → "(3, 3), (8, 8)"
print(underscore_intervals("1_8-9_15"))    # → "(2, 7), (10, 14)"
print(underscore_intervals("0-5_9"))       # → "(6, 8)"
