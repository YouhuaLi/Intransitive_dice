"""
Unified multi-player intransitive dice generator (face-count optimised).

Given a prime p, this builds p dice realising the Paley tournament P(p):

    die i beats die j   <=>   (i - j) mod p is a quadratic residue.

P(p) is a k-paradoxical tournament, so the dice are (k+1)-player intransitive:
for ANY k dice there is another die that beats all of them.  The number of
players is read off OEIS A362137:  [1, 3, 7, 19, 67, 331, 1163]
    p >= 3  -> 2 players (any 1 die beaten)
    p >= 7  -> 3 players (any 2 dice beaten by a 3rd)
    p >= 19 -> 4 players (any 3 dice beaten by a 4th)
    p >= 67 -> 5 players (any 4 dice beaten by a 5th)
    ...

Two construction methods, both based on the same idea: realise the tournament
as the MAJORITY of F linear orders ("voters"), then encode each order as a
block of faces with an offset p*t, so that cross-block comparisons cancel and

    bias(i, j) = sum_t sgn( order_t[i] - order_t[j] ).

Each die ends up with F faces.

  * "circulant" (default): the F = p orders are the p rotations of a single
    base permutation pi.  Reliable and fast for ANY prime (only ~p/2 sign
    constraints to satisfy), but uses p faces per die.

  * "reduce": search (simulated annealing) for the smallest possible number
    of orders F whose majority equals P(p).  Gives far fewer faces
    (e.g. p=19 -> 9 instead of 19; p=7 -> 3), but the search gets expensive
    for large p.

Usage:
    python gen_unified.py <prime>                 # circulant, p faces
    python gen_unified.py <prime> --reduce        # search minimum faces
    python gen_unified.py <prime> --reduce --max-faces 9
    python gen_unified.py <prime> --chain         # chain construction (needs p%8==7)
    python gen_unified.py --players 5             # auto-pick prime for fewest faces

  Method summary (faces per die):
    default        : deterministic circulant, p faces, no search
                     (Bednay & Bozoki 2013, Construction 6); works for any
                     prime p == 3 (mod 4).
    --chain        : chain construction, (p-1)/2 faces; requires p == 7 (mod 8).
    --players N    : auto-picks the smallest prime == 7 (mod 8) with enough
                     vertices and uses --chain -> (p-1)/2 faces
                     (5 players -> 71 dice, 35 faces).
    --reduce       : simulated-annealing search for the fewest faces (small p;
                     e.g. p=19 -> 9 faces, the best known per Bednay-Bozoki 2013).

  References:
    R. L. Graham, J. H. Spencer, A constructive solution to a tournament
      problem, Canad. Math. Bull. 14 (1971) 45-48.
    S. Bozoki, Nontransitive dice sets realizing the Paley tournaments,
      Miskolc Math. Notes 15 (2014) 39-50.   [D_p: p(p-1)/2 faces]
    D. Bednay, S. Bozoki, Constructions for nontransitive dice sets, Proc. 8th
      Japanese-Hungarian Symp. on Discrete Math. (2013) 15-23.  [fewer faces]
"""

import argparse
import itertools as it
import math
import random
import time
from collections import Counter

import numpy as np

A362137 = [1, 3, 7, 19, 67, 331, 1163]


def is_prime(n):
    if n < 2:
        return False
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            return False
    return True


def players_for(p):
    """Number of players = largest k with p >= A362137[k-1], plus the 1-player base."""
    k = 0
    for v in A362137:
        if p >= v:
            k += 1
        else:
            break
    return k  # index in the sequence == number of players


def quadratic_residues(p):
    return set(x * x % p for x in range(1, p))


def paley_target(p):
    QR = quadratic_residues(p)
    T = np.zeros((p, p), dtype=np.int64)
    for i in range(p):
        for j in range(p):
            if i != j:
                T[i][j] = 1 if ((i - j) % p) in QR else -1
    return T


# --------------------------------------------------------------------------
# Method 0: chain construction (only valid when p % 8 == 7), (p-1)/2 faces
# --------------------------------------------------------------------------

def chain_orders(p):
    """The classic quadratic-residue chains; valid iff p % 8 == 7.

    Returns (p-1)/2 permutations of {0,...,p-1}; build_dice then yields dice
    with (p-1)/2 faces each.  The realised tournament is doubly-regular and
    k-paradoxical (though not literally the QR-Paley adjacency).
    """
    if p % 8 != 7:
        raise ValueError(f"chain construction requires p % 8 == 7 (got {p % 8})")
    QR = sorted(quadratic_residues(p))
    start = (p - 1) // 2
    orders = []
    for r in QR:
        ch = [start]
        while len(ch) < p:
            ch.append((ch[-1] - r) % p)
        orders.append(ch)
    return orders


def fewest_faces_prime(players):
    """Smallest prime p == 7 (mod 8) with enough vertices for `players`.

    Such a p admits the deterministic chain construction with (p-1)/2 faces,
    which is far fewer than the circulant p faces (e.g. 5 players: 71 dice,
    35 faces, vs 67 dice / 67 faces)."""
    if players < 1 or players > len(A362137):
        raise ValueError(f"players must be in 1..{len(A362137)}")
    threshold = A362137[players - 1]
    p = threshold
    while True:
        if p % 8 == 7 and is_prime(p):
            return p
        p += 1


# --------------------------------------------------------------------------
# Method 1: deterministic circulant, p faces (Bednay-Bozoki 2013, Construction 6)
# --------------------------------------------------------------------------

def construction6_dice(p):
    """Deterministic n-face realization of the Paley tournament P(p).

    Bednay & Bozoki (2013), Construction 6: any rotationally-symmetric
    (circulant) tournament on n vertices is realizable with n faces, in closed
    form -- no search needed.

    Die k, row i (i = 0..p-1): value 0 if i == k, otherwise +/- ((k-i) mod p),
    with sign + iff die k beats die i (i.e. (i-k) mod p is a quadratic residue).
    Rows carry an additive term i*(2p) so that comparisons between different
    rows cancel and only same-row faces decide the bias.
    """
    QR = quadratic_residues(p)
    spacing = 2 * p  # > 2*(p-1), keeps rows in disjoint bands
    dice = []
    for k in range(p):
        faces = []
        for i in range(p):
            if i == k:
                v = 0
            else:
                l = (k - i) % p
                v = l if (((i - k) % p) in QR) else -l
            faces.append(i * spacing + v)
        dice.append(sorted(faces))
    return dice


# --------------------------------------------------------------------------
# Method 2: minimum-faces search (simulated annealing, O(p) per step)
# --------------------------------------------------------------------------

def sa_orders(p, F, seed=0, iters=2_000_000, restarts=200, t0=4.0, budget=300.0):
    """Find F permutations whose majority tournament equals P(p). Returns orders or None."""
    T = paley_target(p)
    tri = np.triu_indices(p, 1)
    idx = np.arange(p)
    rng = random.Random(seed)
    npr = np.random.default_rng(seed)
    start = time.time()
    for _ in range(restarts):
        if time.time() - start > budget:
            break
        ords = [npr.permutation(p).astype(np.int64) for _ in range(F)]
        M = sum(np.sign(v[:, None] - v[None, :]) for v in ords)
        mism = int(np.sum((np.sign(M) != T)[tri]))
        temp = t0
        stuck = 0
        for _ in range(iters):
            if mism == 0:
                return [v.tolist() for v in ords]
            temp = max(0.05, temp * 0.99997)
            if stuck > 4000:
                temp = t0 * 0.6
                stuck = 0
            t = rng.randrange(F)
            a, b = rng.sample(range(p), 2)
            v = ords[t]
            oa, ob = int(v[a]), int(v[b])
            ma = (idx != a)
            mb = (idx != b) & (idx != a)
            old = int(np.sum(np.sign(M[a])[ma] != T[a][ma])) \
                + int(np.sum(np.sign(M[b])[mb] != T[b][mb]))
            v[a], v[b] = ob, oa
            mask = (idx != a) & (idx != b)
            vk = v[mask]
            dak = np.sign(ob - vk) - np.sign(oa - vk)
            dbk = np.sign(oa - vk) - np.sign(ob - vk)
            M[a, mask] += dak; M[mask, a] -= dak
            M[b, mask] += dbk; M[mask, b] -= dbk
            dab = -2 * np.sign(oa - ob)
            M[a, b] += dab; M[b, a] -= dab
            new = int(np.sum(np.sign(M[a])[ma] != T[a][ma])) \
                + int(np.sum(np.sign(M[b])[mb] != T[b][mb]))
            nm = mism + (new - old)
            if nm <= mism or rng.random() < math.exp((mism - nm) / temp):
                stuck = stuck + 1 if nm >= mism else 0
                mism = nm
            else:
                v[a], v[b] = oa, ob
                M[a, mask] -= dak; M[mask, a] += dak
                M[b, mask] -= dbk; M[mask, b] += dbk
                M[a, b] -= dab; M[b, a] += dab
                stuck += 1
    return None


def minimum_orders(p, seed=0, max_faces=None, budget_per_F=300.0):
    """Try odd F = 3, 5, 7, ... and return the first (smallest) realisation found."""
    cap = max_faces if max_faces is not None else p
    F = 3
    while F <= cap:
        ords = sa_orders(p, F, seed=seed, budget=budget_per_F)
        if ords is not None:
            return F, ords
        print(f"  F={F}: no realisation found within budget, increasing...")
        F += 2
    return None


# --------------------------------------------------------------------------
# Assembly + verification
# --------------------------------------------------------------------------

def build_dice(orders, p):
    F = len(orders)
    return [sorted(int(p * t + orders[t][i]) for t in range(F)) for i in range(p)]


def verify(dice, p, players, check_paradox=True):
    bias = lambda d1, d2: sum((j < i) - (i < j) for i in d1 for j in d2)
    wins = lambda d1, d2: np.sign(bias(d1, d2))

    # Paley P(p) is self-converse, so accept either orientation (QR or its reverse).
    QR = quadratic_residues(p)
    fwd = all(wins(dice[i], dice[j]) == (1 if ((i - j) % p) in QR else -1)
              for i in range(p) for j in range(p) if i != j)
    rev = all(wins(dice[i], dice[j]) == (1 if ((j - i) % p) in QR else -1)
              for i in range(p) for j in range(p) if i != j)
    paley_ok = fwd or rev

    k = players - 1  # coalition size
    paradox_ok = None
    winners_dist = None
    if check_paradox:
        # beats[i] = bitmask of dice i beats; beatenby[j] = bitmask of dice that beat j
        beatenby = [0] * p
        for i in range(p):
            for j in range(p):
                if i != j and bias(dice[i], dice[j]) > 0:
                    beatenby[j] |= (1 << i)
        bad = 0
        dist = Counter()
        for combo in it.combinations(range(p), k):
            common = beatenby[combo[0]]
            for c in combo[1:]:
                common &= beatenby[c]
            n_winners = bin(common).count("1")
            dist[n_winners] += 1
            if n_winners == 0:
                bad += 1
        paradox_ok = (bad == 0)
        winners_dist = dict(sorted(dist.items()))
    return paley_ok, paradox_ok, winners_dist


def main():
    ap = argparse.ArgumentParser(description="Unified intransitive dice generator")
    ap.add_argument("prime", type=int, nargs="?", default=None,
                    help="prime number of dice (>=3); omit when using --players")
    ap.add_argument("--players", type=int, default=None,
                    help="intended player count. Without a prime: auto-pick the "
                         "smallest prime ==7 (mod 8) for this many players and use "
                         "the chain construction. With a prime: OVERRIDE the player "
                         "count to verify against (the A362137 estimate can be wrong, "
                         "e.g. P(103) is 4-player though >=67 suggests 5).")
    ap.add_argument("--chain", action="store_true",
                    help="chain construction, (p-1)/2 faces (requires p %% 8 == 7)")
    ap.add_argument("--reduce", action="store_true",
                    help="search for the minimum number of faces (slow for large p)")
    ap.add_argument("--max-faces", type=int, default=None,
                    help="upper bound on faces to try in --reduce mode")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--budget", type=float, default=60.0,
                    help="seconds per face-count attempt in --reduce mode "
                         "(it scans F=3,5,7,... upward, spending this long on each)")
    ap.add_argument("--no-paradox-check", action="store_true",
                    help="skip the explicit k-paradoxical enumeration")
    ap.add_argument("--show-dice", action="store_true", help="print all face values")
    ap.add_argument("--out", default=None,
                    help="write the dice to a file (one die per line, space-separated)")
    args = ap.parse_args()

    # --- choose the prime, the player count, and the construction method ----
    if args.prime is not None:
        # explicit prime; --players (if given) overrides the player-count estimate
        p = args.prime
        use_chain = args.chain
        if args.players is not None:
            players = args.players
        else:
            players = players_for(p)
    else:
        # no prime: auto-pick the smallest prime ==7 (mod 8) for --players players
        if args.players is None:
            raise SystemExit("provide a prime, or use --players N")
        p = fewest_faces_prime(args.players)
        players = args.players
        use_chain = True
        print(f"--players {args.players}  ->  smallest prime == 7 (mod 8) with enough "
              f"vertices is p = {p}")

    if not is_prime(p) or p < 3:
        raise SystemExit("argument must be a prime >= 3")
    if players < 2:
        raise SystemExit("player count must be >= 2")
    est = players_for(p)
    note = ""
    if args.players is not None and args.prime is not None and players != est:
        note = f"  [overriding A362137 estimate of {est}]"
    print(f"p = {p}  ->  {players} players  "
          f"(any {players-1} dice are beaten by another die){note}")

    if args.reduce:
        print("searching for minimum faces (majority-of-orders, simulated annealing)...")
        res = minimum_orders(p, seed=args.seed, max_faces=args.max_faces,
                              budget_per_F=args.budget)
        if res is None:
            raise SystemExit("no realisation found; raise --max-faces / --budget, "
                             "or drop --reduce to use the default construction")
        faces, orders = res
        dice = build_dice(orders, p)
        method = f"minimum search (F={faces})"
    elif use_chain:
        if p % 8 != 7:
            raise SystemExit(f"chain construction needs p % 8 == 7, but {p} % 8 == {p % 8}; "
                             f"use the default construction or --reduce instead")
        orders = chain_orders(p)
        faces = len(orders)
        dice = build_dice(orders, p)
        method = f"chain (F=(p-1)/2={faces})"
    else:
        dice = construction6_dice(p)
        faces = len(dice[0])
        method = f"deterministic circulant, F=p={faces} (Bednay-Bozoki 2013, Constr. 6)"

    paley_ok, paradox_ok, dist = verify(
        dice, p, players, check_paradox=not args.no_paradox_check)

    print(f"method: {method}")
    print(f"=> {p} dice, {faces} faces each")
    print(f"matches Paley tournament P({p}): {paley_ok}")
    if paradox_ok is not None:
        print(f"{players}-player property verified "
              f"(every {players-1}-coalition beaten): {paradox_ok}")
        print(f"winners-per-coalition distribution: {dist}")
    if args.out:
        with open(args.out, "w") as f:
            for d in dice:
                f.write(" ".join(map(str, d)) + "\n")
        print(f"wrote dice to {args.out}  (verify with: "
              f"python verify_dice_set.py {players} {args.out})")
    if args.show_dice:
        print()
        for i, d in enumerate(dice):
            print(f"Die {i:2d}: " + " ".join(f"{v:3d}" for v in d))

    # Validity is certified by the explicit k-paradoxical enumeration. Note that
    # realizing P(p) does NOT by itself guarantee the property: P(p) is only
    # k-paradoxical for suitable p (e.g. P(103) is not 4-paradoxical), so the
    # enumeration is the real check.
    if paradox_ok is None:
        print("warning: --no-paradox-check set; validity was NOT verified")
    elif not paradox_ok:
        raise SystemExit(
            f"INVALID: the {players}-player property FAILED for p={p} -- some "
            f"{players-1}-coalition is beaten by no other die. P({p}) is not "
            f"{players-1}-paradoxical (being >= the A362137 threshold is not "
            f"sufficient; e.g. P(103) fails). Try a different prime.")


if __name__ == "__main__":
    main()
