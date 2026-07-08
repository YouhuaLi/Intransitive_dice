"""SAT face-minimization for the Paley tournament P(p), rank/voter encoding.

Finds a d-face realization of P(p) (or reports UNSAT).  Options: column-permutation
symmetry breaking (decisive at scale) and an optional equal-sum constraint.

Usage:
    python sat_solve.py <p> <d> [solver] [budget_s] [symbreak 0/1] [eqsum 0/1] [eqsum_enc]

  solver     : pysat solver name (default cadical300; try cadical195, kissat404, glucose42)
  budget_s   : 0 = unbounded (default). NOTE pysat's CaDiCaL ignores this; use OS kill.
  symbreak   : 1 (default) lex-orders adjacent face-columns (d! symmetry). Helps hard/UNSAT.
  eqsum      : 1 forces every die to the balanced sum d*(p*d+1)/2 (kmtotalizer). Default 0.
  eqsum_enc  : cardinality encoding for eqsum (default kmtotalizer; totalizer OOMs at scale).

Encoding: V(X,Y,i,i) = "die X's band-i face > die Y's band-i face"; transitivity per band;
winner takes >= floor(d/2)+1 of the diagonal comparisons.  Values reconstruct as a
permutation of 1..p*d (banded by slot).  A verified SAT solution is written to
paley<p>_<d>face.txt (values-as-permutation).  Self-contained (no repo imports).
"""
import sys, os, time, gc, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver
from lex import add_lex_leq

ENC = {'totalizer': EncType.totalizer, 'mtotalizer': EncType.mtotalizer,
       'kmtotalizer': EncType.kmtotalizer, 'seqcounter': EncType.seqcounter,
       'cardnetwrk': EncType.cardnetwrk, 'sortnetwrk': EncType.sortnetwrk}


def qr_tournament(p):
    Q = {i * i % p for i in range(1, p)}
    return [[1 if (j - i) % p in Q else 0 for j in range(p)] for i in range(p)]


def build_clauses(t, d, symbreak=True, eqsum=False, eqsum_enc='kmtotalizer'):
    n = len(t); pool = IDPool(); clauses = []

    def V(X, Y, i, j):
        if j < i: return pool.id('true')
        if j > i: return pool.id('false')
        return pool.id(('v', X, Y, i, j)) if X < Y else -pool.id(('v', Y, X, j, i))

    for X in range(n):
        for i in range(d):
            for j in range(d):
                lit = V(X, X, i, j); clauses.append([lit] if i >= j else [-lit])
    clauses.append([pool.id('true')]); clauses.append([-pool.id('false')])
    for X in range(n):
        for Y in range(X + 1, n):
            for i in range(d):
                V(X, Y, i, i)
    for X in range(n):
        for Y in range(n):
            for Z in range(n):
                if Z in (X, Y): continue
                for i in range(d):
                    clauses.append([-V(X, Y, i, i), -V(Y, Z, i, i), V(X, Z, i, i)])
    thr = d // 2 + 1
    for X in range(n):
        for Y in range(n):
            if X == Y or not t[X][Y]: continue
            lits = [V(X, Y, i, i) for i in range(d)]
            clauses.extend(CardEnc.atleast(lits=lits, bound=thr,
                                           encoding=EncType.totalizer, vpool=pool).clauses)
    if eqsum:
        total = n * d * (n * d + 1) // 2
        assert total % n == 0
        card_target = (total // n) - n * (d * (d - 1) // 2) - d   # exactly (d+... ) diag lits true
        for X in range(n):
            lits = [V(X, Y, i, i) for i in range(d) for Y in range(n) if Y != X]
            clauses.extend(CardEnc.atmost(lits=lits, bound=card_target,
                                          encoding=ENC[eqsum_enc], vpool=pool).clauses)
    ncore = len(clauses)
    if symbreak:
        pairs = [(X, Y) for X in range(n) for Y in range(X + 1, n)]
        cols = [[V(X, Y, i, i) for (X, Y) in pairs] for i in range(d)]
        for i in range(d - 1):
            add_lex_leq(cols[i], cols[i + 1], pool, clauses, i)
    return clauses, pool, V, n, len(clauses) - ncore


def reconstruct(model, V, n, d):
    ms = set(model)
    return [sorted(sum(1 for Y in range(n) for j in range(d) if V(X, Y, i, j) in ms)
                   for i in range(d)) for X in range(n)]


def verify(dice, t):
    n = len(dice)
    for i in range(n):
        for j in range(n):
            if i == j: continue
            w = sum(1 for a in dice[i] for b in dice[j] if a > b)
            if bool(t[i][j]) != (2 * w > len(dice[i]) * len(dice[j])):
                return False
    return True


def main():
    p = int(sys.argv[1]); d = int(sys.argv[2])
    solver = sys.argv[3] if len(sys.argv) > 3 else 'cadical300'
    budget = float(sys.argv[4]) if len(sys.argv) > 4 else 0
    symbreak = (sys.argv[5] != '0') if len(sys.argv) > 5 else True
    eqsum = (sys.argv[6] != '0') if len(sys.argv) > 6 else False
    enc = sys.argv[7] if len(sys.argv) > 7 else 'kmtotalizer'

    t = qr_tournament(p)
    print(f"[{solver}] P_{p} d={d} SB={symbreak} eqsum={eqsum}", flush=True)
    t0 = time.time()
    clauses, pool, V, n, sb = build_clauses(t, d, symbreak, eqsum, enc)
    print(f"  build {time.time()-t0:.1f}s clauses={len(clauses)} (sb={sb}) vars={pool.top}", flush=True)
    s = Solver(name=solver, bootstrap_with=clauses, use_timer=True)
    del clauses; gc.collect()
    timed_out = [False]
    if budget > 0:
        def interrupt():
            timed_out[0] = True
            try: s.interrupt()
            except Exception: pass         # pysat CaDiCaL doesn't support interrupt
        tm = threading.Timer(budget, interrupt); tm.start()
        res = s.solve_limited(expect_interrupt=True); tm.cancel()
    else:
        res = s.solve()
    print(f"  solve {s.time():.1f}s result={res} timed_out={timed_out[0]}", flush=True)
    if res is True:
        dice = reconstruct(s.get_model(), V, n, d)
        ok = verify(dice, t)
        allv = sorted(v for x in dice for v in x)
        sums = [sum(x) for x in dice]
        print(f"  SAT verified={ok} perm(1..{n*d})={allv==list(range(1,n*d+1))} "
              f"sum=[{min(sums)},{max(sums)}]", flush=True)
        if ok:
            fn = f"paley{p}_{d}face.txt"
            with open(fn, "w") as f:
                for x in dice: f.write(" ".join(map(str, x)) + "\n")
            print(f"  wrote {fn}", flush=True)
    elif res is False:
        print(f"  UNSAT: no d={d} realization of P({p})", flush=True)
    else:
        print("  UNKNOWN (budget)", flush=True)
    s.delete()


if __name__ == "__main__":
    main()
