import numpy as np
from collections import Counter
import itertools as it
from fractions import Fraction
from tabulate import tabulate
import sys

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(np.sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

if len(sys.argv) != 2:
    print("Usage: python print_cycle.py <prime_number_greater_than_5>")
    sys.exit(1)

try:
    dice_amount = int(sys.argv[1])
except ValueError:
    print("The argument must be an integer.")
    sys.exit(1)

if not is_prime(dice_amount) or dice_amount < 7:
    print("The argument must be a prime number greater than 5.")
    sys.exit(1)

OEIS_A362137 = [1, 3, 7, 19, 67, 331, 1163] # https://oeis.org/A362137 Smallest size of an n-paradoxical tournament built as a directed Paley graph. 

index = 0
for i, val in enumerate(OEIS_A362137):
    if dice_amount < val:
        break
    index = i + 1
players_amount = index
print(f"Players amount: {players_amount}")

residues = sorted(set([x**2 % dice_amount for x in range(1, dice_amount)]))
#print(residues)
chains = []

if dice_amount % 8 == 7:
    for r in residues:
        n = (dice_amount - 1) // 2
        chain =[n]
        while len(chain) < dice_amount:
            chain.append( (chain[-1]-r) % dice_amount )
        chains.append(chain)
else:
    for n in range(0, dice_amount):
        for r in residues:
            chain = [n]
            while len(chain) < dice_amount:
                chain.append( (chain[-1]-r) % dice_amount )
            chains.append(chain)

#print(tabulate(chains))
#print(len(chains))
transposed_chains = list(map(list, zip(*chains)))

sum_of_last_row = -1
dice_face_values = []

for row in chains:
    face_vale = [i + sum_of_last_row + 1 for i in row]
    dice_face_values.append(face_vale)
    sum_of_last_row = max(face_vale)

dice = list(map(list, zip(*dice_face_values)))

opponents = players_amount - 1

#Let's also define a win dictionary:
d_wins = lambda d: {i[0]:sorted(j[0] for j in d if wins(i,j)>0) for i in sorted(d)}

# a function which tells us by how much one wins over another
bias = lambda d1, d2: sum([(j<i)-(i<j) for i in d1 for j in d2])

# the sign of the win function, negative means the second die wins, positive means the first
wins = lambda d1,d2: np.sign(bias(d1,d2))
select_dice_that_beat = lambda i: [j[0] for j in dice if i!=j if wins(i,j)>0]
die_that_beats_all = lambda q: [j for j in range(n) if all(j in k for k in q)]
has_unbeaten_dice = lambda d: [q for q in it.combinations([select_dice_that_beat(i) for i in d], opponents) if not die_that_beats_all(q)]

d = dice

# Check if there are any duplicate numbers in d
duplicates = [item for sublist in d for item in sublist if d.count(item) > 1]
assert not duplicates
w = d_wins(d)
#print(w)

# define a function that tells you which die will beat any three dice that are given to you.
def which_beats(dice):
    return {i for i,j in w.items() if all(die in j for die in dice)}

#all_dice_win = lambda w: all(len(which_beats(i)) for i in it.combinations(list(w), opponents))
#make sure that all combinations of dice have a winning solution.
#assert all_dice_win(w)

print(f"found a dice set of size {dice_amount} of {len(dice[0])} faces each with {players_amount} players")
print("below is the dice set. Each column is a die, each row is one value of the die.")
print(tabulate(dice_face_values))
