"""Residual-SAT hybrid for Paley P(p): bilevel head (first K layers = 2K voters, each
covered arc +2, residual arc 0) + M SAT voters that must give residual arcs strict
majority while keeping covered arcs from losing by >=3 (weaker bound, exploiting the +2).
Total faces = 2K + M (odd). Usage: python hybrid.py <p> <K> <M> [solver] [budget_s]"""
import sys, os, time, gc, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bilevel"))
import numpy as np
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver
from lex import add_lex_leq
from bilevel_balanced import decompose, bits, paley_out


def qr_tournament(p):
    Q = {i*i % p for i in range(1, p)}
    return [[1 if (j-i) % p in Q else 0 for j in range(p)] for i in range(p)]


def head_orders(p, K, seeds=32):
    """First K bilevel layers -> list of 2K orders (each a permutation of 0..p-1,
    front=highest). Returns (orders, covered) where covered[X] = bitmask of Y with
    head margin +2 for arc X->Y."""
    layers, total, cov = decompose(p, seeds, 10*p)
    layers = layers[:K]
    orders = []
    for blocks in layers:
        r1 = []; r2 = []
        for (A, B) in blocks:
            r1 += sorted(bits(A)) + sorted(bits(B))
        for (A, B) in reversed(blocks):
            r2 += sorted(bits(A), reverse=True) + sorted(bits(B), reverse=True)
        orders.append(r1); orders.append(r2)
    # covered = arcs with head margin +2
    R = len(orders)
    pos = np.zeros((R, p), dtype=np.int32)
    for r, row in enumerate(orders):
        for idx, v in enumerate(row): pos[r, v] = idx
    before = np.zeros((p, p), dtype=np.int32)
    for r in range(R):
        pr = pos[r]; before += (pr[:, None] < pr[None, :]).astype(np.int32)
    margin = before - before.T          # margin[X,Y] = (#X before Y) - (#Y before X)
    covered = [0]*p
    for X in range(p):
        m = 0
        for Y in range(p):
            if X != Y and margin[X, Y] == 2:   # head gave +2 (covered arc X->Y)
                m |= (1 << Y)
        covered[X] = m
    return orders, covered, R


def build_hybrid(t, M, covered, symbreak=True):
    n = len(t); pool = IDPool(); clauses = []
    def V(X, Y, i, j):
        if j < i: return pool.id('true')
        if j > i: return pool.id('false')
        return pool.id(('v', X, Y, i, j)) if X < Y else -pool.id(('v', Y, X, j, i))
    for X in range(n):
        for i in range(M):
            for j in range(M):
                lit = V(X, X, i, j); clauses.append([lit] if i >= j else [-lit])
    clauses.append([pool.id('true')]); clauses.append([-pool.id('false')])
    for X in range(n):
        for Y in range(X+1, n):
            for i in range(M): V(X, Y, i, i)
    for X in range(n):
        for Y in range(n):
            for Z in range(n):
                if Z in (X, Y): continue
                for i in range(M):
                    clauses.append([-V(X, Y, i, i), -V(Y, Z, i, i), V(X, Z, i, i)])
    strict = M//2 + 1     # residual bound
    weak   = M//2         # covered bound (one less; +2 head rescues)
    for X in range(n):
        for Y in range(n):
            if X == Y or not t[X][Y]: continue
            bound = weak if ((covered[X] >> Y) & 1) else strict
            if bound <= 0: continue
            lits = [V(X, Y, i, i) for i in range(M)]
            clauses.extend(CardEnc.atleast(lits=lits, bound=bound,
                                           encoding=EncType.totalizer, vpool=pool).clauses)
    if symbreak:
        pairs = [(X, Y) for X in range(n) for Y in range(X+1, n)]
        cols = [[V(X, Y, i, i) for (X, Y) in pairs] for i in range(M)]
        for i in range(M-1):
            add_lex_leq(cols[i], cols[i+1], pool, clauses, i)
    return clauses, pool, V, n


def sat_orders_from_model(model, V, n, M):
    """Each band i -> order of dice by descending (#wins in band i). Ties broken by id.
    Returns M orders (front=highest)."""
    ms = set(model)
    orders = []
    for i in range(M):
        wins = [(sum(1 for Y in range(n) if Y != X and V(X, Y, i, i) in ms), X) for X in range(n)]
        # higher wins in this band => higher value => earlier in order
        order = [X for _, X in sorted(wins, key=lambda z: (-z[0], z[1]))]
        orders.append(order)
    return orders


def verify_full(all_orders, p):
    R = len(all_orders)
    pos = np.zeros((R, p), dtype=np.int32)
    for r, row in enumerate(all_orders):
        for idx, v in enumerate(row): pos[r, v] = idx
    before = np.zeros((p, p), dtype=np.int32)
    for r in range(R):
        pr = pos[r]; before += (pr[:, None] < pr[None, :]).astype(np.int32)
    Q = {i*i % p for i in range(1, p)}
    paley = np.array([[1 if (j-i) % p in Q else 0 for j in range(p)] for i in range(p)], dtype=bool)
    mism = ties = 0
    for i in range(p):
        for j in range(p):
            if i == j: continue
            if 2*before[i, j] == R: ties += 1
            if bool(2*before[i, j] > R) != bool(paley[i, j]): mism += 1
    return mism, ties, R


def main():
    p = int(sys.argv[1]); K = int(sys.argv[2]); M = int(sys.argv[3])
    solver = sys.argv[4] if len(sys.argv) > 4 else 'cadical300'
    budget = float(sys.argv[5]) if len(sys.argv) > 5 else 0
    symbreak = (sys.argv[6] != '0') if len(sys.argv) > 6 else True
    t = qr_tournament(p)
    t0 = time.time()
    orders, covered, R = head_orders(p, K)
    ncov = sum(c.bit_count() for c in covered)
    narcs = sum(sum(row) for row in t)
    print(f"P({p}) K={K} -> {R} head voters; covered {ncov}/{narcs} arcs; "
          f"residual {narcs-ncov} ({(narcs-ncov)/narcs*100:.1f}%)  M={M}  total faces={R+M}", flush=True)
    clauses, pool, V, n = build_hybrid(t, M, covered, symbreak)
    print(f"  SAT build {time.time()-t0:.1f}s clauses={len(clauses)} vars={pool.top}", flush=True)
    s = Solver(name=solver, bootstrap_with=clauses, use_timer=True)
    del clauses; gc.collect()
    if budget > 0:
        def interrupt():
            try: s.interrupt()
            except Exception: pass
        tm = threading.Timer(budget, interrupt); tm.start()
        res = s.solve_limited(expect_interrupt=True); tm.cancel()
    else:
        res = s.solve()
    print(f"  SAT solve {s.time():.1f}s result={res}", flush=True)
    if res is True:
        sat_ord = sat_orders_from_model(s.get_model(), V, n, M)
        allo = orders + sat_ord
        mism, ties, Rf = verify_full(allo, p)
        ok = (mism == 0 and ties == 0)
        print(f"  COMBINED {Rf} faces: valid={ok} (mism={mism}, ties={ties})", flush=True)
        if ok:
            dice = [[] for _ in range(p)]
            for r, row in enumerate(allo):
                for idx, v in enumerate(row):
                    dice[v].append(r*p + (p-idx))
            dice = [sorted(d) for d in dice]
            fn = f"paley{p}_{Rf}face_hybrid.txt"
            with open(fn, "w") as f:
                for d in dice: f.write(" ".join(map(str, d)) + "\n")
            print(f"  wrote {fn}", flush=True)
    elif res is False:
        print("  UNSAT at this (K,M)", flush=True)
    else:
        print("  UNKNOWN (budget)", flush=True)
    s.delete()


if __name__ == "__main__":
    main()
