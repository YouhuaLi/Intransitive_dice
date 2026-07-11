"""
Verify a dice set is a valid 6-player intransitive dice set, via the
domination-number characterization (the literal C(n,5) coalition enumeration
of verify_dice_set.py is infeasible for n=331: C(331,5) ~ 3.3e9).

Equivalence (same `bias`/`wins` relation as gen_intransitive_dice.py /
verify_dice_set.py):

    A coalition S of `opponents = players-1` dice has NO common beater
    <=>  every other die is beaten by some die in S
    <=>  S is a DOMINATING SET of the dominance tournament.

So the set is a valid n-player set  <=>  the tournament has NO dominating set
of size (n-1), i.e. domination number  gamma >= n.  For 6 players: gamma >= 6,
i.e. no dominating set of size 5.

Proving "no size-5 dominating set" over 331 vertices is only tractable with
symmetry breaking.  If an automorphism certificate is supplied (a permutation
that is a single n-cycle and preserves every arc), the tournament is
vertex-transitive, so a size-5 dominating set exists iff one exists containing
vertex 0 -- reducing the search ~n-fold.  The certificate itself is CHECKED
here in O(n^2), so the result stays rigorous.

Usage:
    python verify_6player_domination.py <dice_file> [automorphism_cert_file]

Prints VALID / INVALID with statistics.
"""
import sys, time
import numpy as np


def load_dice(path):
    dice = []
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            dice.append([int(x) for x in line.split()])
    return dice


def build_tournament(dice):
    """Dominance relation using the exact bias/wins of the repo."""
    n = len(dice)
    A = np.array(dice)
    B = np.zeros((n, n), dtype=np.int64)
    for k in range(A.shape[1]):               # one column per voter; bands are disjoint
        c = A[:, k]
        B += np.sign(c[:, None] - c[None, :]).astype(np.int8)
    np.fill_diagonal(B, 0)
    return B  # bias matrix; wins(i,j) = sign(B[i,j]); i beats j iff B[i,j] > 0


def check_automorphism(beats, cert):
    n = beats.shape[0]
    sigma = np.array(cert, dtype=int)
    if sorted(sigma.tolist()) != list(range(n)):
        return False, "not a permutation of 0..n-1"
    # single n-cycle => the group <sigma> acts transitively on the vertices
    seen, x, c = set(), 0, 0
    while x not in seen:
        seen.add(x); x = int(sigma[x]); c += 1
    if c != n:
        return False, "permutation is not a single %d-cycle (transitivity not established)" % n
    if not np.array_equal(beats, beats[np.ix_(sigma, sigma)]):
        return False, "not arc-preserving (not an automorphism)"
    return True, "verified %d-cycle automorphism => vertex-transitive" % n


def no_dom_set_size5(beats, transitive):
    """Return (no_size5_domset, witness_or_None).

    Complete branch-and-bound.  If `transitive`, fix vertex 0 in the set
    (sound by vertex-transitivity); else search all first vertices (slow)."""
    n = beats.shape[0]
    FULL = (1 << n) - 1
    cover = [0] * n                            # cover[d] = {d} U out-neighbours(d)
    for d in range(n):
        m = 1 << d
        for u in np.nonzero(beats[d])[0].tolist():
            m |= (1 << u)
        cover[d] = m
    maxcov = max(c.bit_count() for c in cover)
    doms = [[] for _ in range(n)]              # dominators of e = {e} U in-neighbours(e)
    for d in range(n):
        c = cover[d]
        while c:
            b = c & (-c); doms[b.bit_length() - 1].append(d); c ^= b

    found = [None]
    def dominatable(undom, budget, chosen):
        if undom == 0:
            found[0] = list(chosen); return True
        if budget == 0:
            return False
        if (undom.bit_count() + maxcov - 1) // maxcov > budget:   # lower-bound prune
            return False
        # branch on the still-undominated vertex with the fewest dominators
        cc = undom; beste = -1; bl = 1 << 30
        while cc:
            b = cc & (-cc); e = b.bit_length() - 1; cc ^= b
            if len(doms[e]) < bl:
                bl = len(doms[e]); beste = e
        for d in doms[beste]:
            if dominatable(undom & ~cover[d], budget - 1, chosen + [d]):
                return True
        return False

    if transitive:
        exists = dominatable(FULL & ~cover[0], 4, [0])   # vertex 0 fixed in the set
    else:
        exists = dominatable(FULL, 5, [])
    return (not exists), found[0]


def greedy_dom_set(beats):
    n = beats.shape[0]; FULL = (1 << n) - 1
    cover = []
    for d in range(n):
        m = 1 << d
        for u in np.nonzero(beats[d])[0].tolist():
            m |= (1 << u)
        cover.append(m)
    undom = FULL; chosen = []
    while undom:
        best = max(range(n), key=lambda d: (cover[d] & undom).bit_count())
        chosen.append(best); undom &= ~cover[best]
    return chosen


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python verify_6player_domination.py <dice_file> [automorphism_cert_file]")
    dice = load_dice(sys.argv[1])
    n = len(dice)
    faces = sorted(set(len(d) for d in dice))
    B = build_tournament(dice)

    iu = np.triu_indices(n, 1)
    ties = int((B[iu] == 0).sum())
    outdeg = (B > 0).sum(1)
    beats = B > 0

    print("dice           : %d" % n)
    print("faces per die  : %s" % (faces[0] if len(faces) == 1 else faces))
    print("bias range     : [%d, %d]" % (B.min(), B.max()))
    print("tied pairs     : %d" % ties)
    print("out-degrees    : min %d max %d" % (outdeg.min(), outdeg.max()))
    if ties:
        print("INVALID: ties present; not a tournament (a coalition may have no strict beater).")
        sys.exit(1)

    transitive = False
    if len(sys.argv) >= 3:
        cert = [int(x) for x in open(sys.argv[2]).read().split()]
        ok, msg = check_automorphism(beats, cert)
        print("automorphism   : %s" % msg)
        transitive = ok
        if not ok:
            print("  (certificate rejected; falling back to full search)")

    t = time.time()
    no5, witness = no_dom_set_size5(beats, transitive)
    dt = time.time() - t
    if not no5:
        print("INVALID 6-player: found a dominating set of size 5 (coalition with no beater): %s  (%.1fs)"
              % (witness, dt))
        sys.exit(1)

    g6 = greedy_dom_set(beats)
    print("proof          : no dominating set of size 5 exists  =>  gamma >= 6  (%.1fs)" % dt)
    print("               : explicit dominating set of size %d exists (so gamma is exactly 6 if =6): %s"
          % (len(g6), g6))
    print("VALID 6-player intransitive dice set.")
    print("  every coalition of 5 dice is beaten by some other die (checked via gamma >= 6).")
    sys.exit(0)


if __name__ == "__main__":
    main()
