import itertools
import string

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

# Example usage:
unique_strings = generate_unique_strings(100)
print(unique_strings)
