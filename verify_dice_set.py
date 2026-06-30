"""
Verify whether a dice set is a valid n-player intransitive dice set.

Usage:
    python verify_dice_set.py <player_count> <dice_set_file>

The dice file has one die per line; a line is the die's face values separated
by spaces, e.g.:

    0 19 38 57
    18 34 52 70
    ...

Validity (n players, following gen_intransitive_dice.py):
    Let opponents = n - 1.  The set is a valid n-player set iff for EVERY
    coalition of `opponents` dice there exists another die that beats all of
    them (an (n-1)-paradoxical tournament).  This is exactly the `all_dice_win`
    check from gen_intransitive_dice.py.

If the set is invalid, the offending coalitions (and why) are printed.
"""

import itertools as it
import math
import sys

import numpy as np


def load_dice(path):
    dice = []
    try:
        with open(path) as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    dice.append([int(x) for x in line.split()])
                except ValueError:
                    sys.exit(f"error: line {lineno} has a non-integer value: {line!r}")
    except OSError as e:
        sys.exit(f"error: cannot read dice file: {e}")
    return dice


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: python verify_dice_set.py <player_count> <dice_set_file>")
    try:
        players = int(sys.argv[1])
    except ValueError:
        sys.exit("error: player_count must be an integer")

    dice = load_dice(sys.argv[2])
    n = len(dice)
    opponents = players - 1

    # --- structural sanity checks --------------------------------------
    reasons = []
    if players < 2:
        reasons.append(f"player_count must be >= 2 (got {players})")
    if n == 0:
        reasons.append("dice file contains no dice")
    elif n <= opponents:
        reasons.append(
            f"need more than {opponents} dice for {players} players "
            f"(a coalition of {opponents} plus one die to beat it), but only {n} provided")
    if reasons:
        print(f"INVALID {players}-player dice set:")
        for r in reasons:
            print(f"  - {r}")
        sys.exit(1)

    # --- win relation, using the lambdas from gen_intransitive_dice.py --
    bias = lambda d1, d2: sum((j < i) - (i < j) for i in d1 for j in d2)
    wins = lambda d1, d2: np.sign(bias(d1, d2))

    # d_wins, keyed by die index: w[i] = sorted list of dice that die i beats
    w = {i: sorted(j for j in range(n) if i != j and wins(dice[i], dice[j]) > 0)
         for i in range(n)}

    # which_beats(coalition): the set of dice that beat EVERY die in the coalition
    def which_beats(coalition):
        return {i for i, beaten in w.items() if all(c in beaten for c in coalition)}

    # all_dice_win: every coalition of `opponents` dice must have at least one beater.
    # (Implemented with bitmasks so it scales, but identical in meaning.)
    beatenby = [0] * n            # beatenby[j] = bitmask of dice that beat die j
    for i in range(n):
        for j in w[i]:
            beatenby[j] |= (1 << i)

    failing = []
    for coalition in it.combinations(range(n), opponents):
        common = beatenby[coalition[0]]
        for c in coalition[1:]:
            common &= beatenby[c]
        if common == 0:
            failing.append(coalition)

    total = math.comb(n, opponents)
    tie_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)
                 if bias(dice[i], dice[j]) == 0]

    # --- verdict --------------------------------------------------------
    if not failing:
        print(f"VALID {players}-player intransitive dice set.")
        print(f"  dice           : {n}")
        face_counts = sorted(set(len(d) for d in dice))
        print(f"  faces per die  : {face_counts[0] if len(face_counts)==1 else face_counts}")
        print(f"  coalitions     : checked all C({n},{opponents}) = {total}; "
              f"each is beaten by at least one other die")
        if tie_pairs:
            print(f"  note           : {len(tie_pairs)} tied die-pair(s) (bias 0, neither wins)")
        sys.exit(0)

    print(f"INVALID {players}-player dice set.")
    print(f"  reason: {len(failing)} of {total} coalitions of {opponents} dice are "
          f"beaten by NO other die (the {players}-th player cannot win).")
    if tie_pairs:
        print(f"  note  : {len(tie_pairs)} tied die-pair(s) exist (bias 0); ties may cause this.")
    print("  failing coalitions (die indices, 0-based):")
    for coalition in failing[:10]:
        # explain: the best any other die can do is beat only some of the coalition
        best_cover = 0
        for i in range(n):
            if i in coalition:
                continue
            cover = sum(1 for c in coalition if c in w[i])
            best_cover = max(best_cover, cover)
        print(f"    {tuple(coalition)} -> no die beats all {opponents}; "
              f"best any other die does is beat {best_cover}/{opponents}")
    if len(failing) > 10:
        print(f"    ... and {len(failing) - 10} more")
    sys.exit(1)


if __name__ == "__main__":
    main()
