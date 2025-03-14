import random

n = random.randint(1, 300)
permutation = list(range(1, n + 1))
random.shuffle(permutation)

print(f"Random n: {n}")
print("Shuffled list:", permutation)