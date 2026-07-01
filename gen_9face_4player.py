"""
Generate a 4-player intransitive dice set: 19 dice, 9 faces each.

Background
----------
For 4 players you need at least 19 dice (OEIS A362137), and the dominance
relation must form a 3-paradoxical tournament: for ANY 3 dice there is a 4th
die that beats all three.  The Paley tournament P(19) -- i beats j iff
(i - j) mod 19 is a quadratic residue -- is such a tournament.

The original gen_intransitive_dice.py realises P(19) with 171 faces per die.
This script realises the SAME tournament with only 9 faces per die.

Construction
------------
We express P(19) as the MAJORITY of F = 9 linear orders ("voters").  Each
order t is a permutation `orders[t]` of {0,...,18}; `orders[t][i]` is the rank
of die i in that order.  Die i then gets one face per order:

    die_i = { 19 * t + orders[t][i] : t = 0 .. 8 }

The "19 * t" offset makes faces from different orders occupy disjoint ranges,
so cross-order comparisons cancel out and

    bias(i, j) = sum_t sgn( orders[t][i] - orders[t][j] )                (1)

i.e. die i beats die j exactly when a majority of the 9 orders rank i above j.
We search (simulated annealing) for 9 orders whose majority relation (1)
equals P(19).  The search is seeded, so the output is reproducible.

Note: 9 faces is far fewer than 171, but the winning margin is correspondingly
smaller (max win probability ~53%) than the 171-face balanced set (~59.3%).
"""

import numpy as np
import itertools as it
from collections import Counter
import random
import math


def quadratic_residues(p):
    return set(x * x % p for x in range(1, p))


def build_target(p):
    """Paley tournament: T[i][j] = +1 if i beats j, i.e. (i-j) mod p is a QR."""
    QR = quadratic_residues(p)
    T = np.zeros((p, p), dtype=int)
    for i in range(p):
        for j in range(p):
            if i != j:
                T[i][j] = 1 if ((i - j) % p) in QR else -1
    return T


def order_sign(v):
    """Pairwise sign matrix sgn(v[i] - v[j]) for one order's rank vector v."""
    return np.sign(v[:, None] - v[None, :])


def find_orders(p, faces, seed=0, restarts=60, iters=150000, t0=2.5):
    """Simulated annealing for `faces` permutations whose majority equals P(p)."""
    T = build_target(p)
    mask = ~np.eye(p, dtype=bool)

    def cost(M):
        s = np.sign(M)
        return int(np.sum(s[mask] != T[mask])) + int(np.sum(s[mask] == 0))

    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    best = None
    for _ in range(restarts):
        orders = [np_rng.permutation(p) for _ in range(faces)]
        M = sum(order_sign(v) for v in orders)
        c = cost(M)
        for k in range(iters):
            if c == 0:
                return [v.tolist() for v in orders]
            temp = t0 * (1 - k / iters) + 0.02
            t = rng.randrange(faces)
            a, b = rng.sample(range(p), 2)
            v = orders[t]
            old = order_sign(v)
            v[a], v[b] = v[b], v[a]
            new = order_sign(v)
            M2 = M - old + new
            c2 = cost(M2)
            if c2 <= c or rng.random() < math.exp((c - c2) / temp):
                M, c = M2, c2
            else:
                v[a], v[b] = v[b], v[a]  # revert
        if best is None or c < best[0]:
            best = (c, [v.tolist() for v in orders])
    raise RuntimeError(f"no realization found with {faces} faces "
                       f"(best mismatch={best[0]}); try another seed or more iters")


def build_dice(orders, p):
    """die_i = sorted({ p*t + orders[t][i] : t }).  All p*faces values distinct."""
    faces = len(orders)
    return [sorted(p * t + orders[t][i] for t in range(faces)) for i in range(p)]


# --- verification using the exact checks from the repository ---------------

def verify(dice, p, players):
    opponents = players - 1

    bias = lambda d1, d2: sum((j < i) - (i < j) for i in d1 for j in d2)
    wins = lambda d1, d2: np.sign(bias(d1, d2))

    # win dictionary keyed by die index: w[i] = list of dice that die i beats
    w = {i: sorted(j for j in range(p) if i != j and wins(dice[i], dice[j]) > 0)
         for i in range(p)}

    def which_beats(chosen):
        return {i for i, beaten in w.items() if all(c in beaten for c in chosen)}

    # every coalition of `opponents` dice must have at least one die that beats all
    all_dice_win = all(len(which_beats(c)) for c in it.combinations(list(w), opponents))

    # cross-check: tournament must equal Paley P(p), i.e. i beats j iff (i-j) is a QR
    QR = quadratic_residues(p)
    paley_ok = all(wins(dice[i], dice[j]) == (1 if ((i - j) % p) in QR else -1)
                   for i in range(p) for j in range(p) if i != j)

    winners = Counter(len(which_beats(c)) for c in it.combinations(list(w), opponents))
    biases = sorted(set(bias(dice[i], dice[j])
                        for i in range(p) for j in range(p) if i != j))
    return all_dice_win, paley_ok, winners, biases


def main():
    p = 19
    players = 4
    faces = 9

    orders = find_orders(p, faces, seed=0)
    #print(orders)
    dice = build_dice(orders, p)

    all_dice_win, paley_ok, winners, biases = verify(dice, p, players)

    print(f"{players}-player intransitive dice: {p} dice, {len(dice[0])} faces each")
    print()
    for i, d in enumerate(dice):
        print(f"Die {i:2d}: " + " ".join(f"{v:3d}" for v in d))
    print()
    print(f"matches Paley tournament P({p}): {paley_ok}")
    print(f"all_dice_win (every {players-1}-coalition is beaten by some die): {all_dice_win}")
    print(f"winners-per-coalition distribution: {dict(sorted(winners.items()))}")
    max_win_prob = 0.5 + max(biases) / (2 * faces * faces)
    print(f"bias values: {biases}  ->  max win probability ~ {max_win_prob:.4f}")
    assert all_dice_win and paley_ok


if __name__ == "__main__":
    main()
