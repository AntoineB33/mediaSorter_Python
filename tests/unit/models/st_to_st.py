import re

def get_intervals(s):
    parts = s.split('|')
    left_str = parts[0]
    right_str = parts[1] if len(parts) > 1 else ""
    
    def extract_numbers(s_part):
        num_str = ''
        numbers = []
        for char in s_part:
            if char.isdigit() or char == '-':
                num_str += char
            else:
                if num_str != '' and num_str != '-':
                    numbers.append(int(num_str))
                num_str = ''
        if num_str != '' and num_str != '-':
            numbers.append(int(num_str))
        return numbers

    left_numbers = extract_numbers(left_str)
    right_numbers = extract_numbers(right_str)
    
    intervals = []
    
    if left_numbers:
        first_left_neg = -left_numbers[0]
        intervals.append(f"(-float('inf'), {first_left_neg-1})")
    else:
        if right_numbers:
            intervals.append(f"(-float('inf'), {right_numbers[0]-1})")
        else:
            intervals.append(f"(-float('inf'), float('inf'))")
    
    if left_numbers and right_numbers:
        last_left_neg = -left_numbers[-1]
        intervals.append(f"({last_left_neg+1}, {right_numbers[0]-1})")
    
    for i in range(len(right_numbers) - 1):
        intervals.append(f"({right_numbers[i]+1}, {right_numbers[i+1]-1})")
    
    if right_numbers:
        last_right = right_numbers[-1]
        if right_str.endswith('-'):
            pass
        else:
            intervals.append(f"({last_right+1}, float('inf'))")
    else:
        if left_numbers:
            last_left_neg = -left_numbers[-1]
            intervals.append(f"({last_left_neg+1}, float('inf'))")
    
    return ", ".join(intervals)

# --- Testing with the provided examples ---
string = "_6-2_[55]_4-7_9-"
print(f'Input: "{string}"')
print(f'Output: "{get_intervals(string)}"\n')

string = "_[140]-1_8-9_"
print(f'Input: "{string}"')
print(f'Output: "{get_intervals(string)}"\n')

string = "_[78]-"
print(f'Input: "{string}"')
print(f'Output: "{get_intervals(string)}"\n')

string = "_5-[2]_"
print(f'Input: "{string}"')
print(f'Output: "{get_intervals(string)}"\n')

string = "_[3]-1_"
print(f'Input: "{string}"')
print(f'Output: "{get_intervals(string)}"\n')
