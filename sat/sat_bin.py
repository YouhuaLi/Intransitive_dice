"""Compact BINARY-position SAT encoding for Paley P(p) as majority of M voters.
Positions pos(X,i) in ceil(log2 n) bits; LT(X,Y,i)=[pos(X,i)<pos(Y,i)] via an
MSB->LSB comparator chain; distinctness via one clause/pair/band. ~O(n^2 * M * log n)
clauses (vs relational O(n^3 * M)) -> memory-feasible at large p.
Supports pure (all arcs strict majority) and hybrid (per-arc weak/strict bound via `covered`).
Usage: python sat_bin.py <p> <M> [solver] [budget_s]"""
import sys, os, time, gc, math, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


def qr_tournament(p):
    Q = {i*i % p for i in range(1, p)}
    return [[1 if (j-i) % p in Q else 0 for j in range(p)] for i in range(p)]


def build_binary(t, M, covered=None):
    """covered: optional list where (covered[X]>>Y)&1 means arc X->Y has head margin +2
    (weak bound). If None, all arcs use the strict majority bound (pure SAT)."""
    n = len(t); bb = max(1, math.ceil(math.log2(n)))
    pool = IDPool(); clauses = []
    TRUE = pool.id('TRUE'); clauses.append([TRUE])

    def A(X, i, b):                      # position bit b of die X in band i
        return pool.id(('p', X, i, b))

    def EQ(a, lit_a, lit_b):             # returns var z <=> (lit_a <=> lit_b)
        z = pool.id(('eq',) + a)
        clauses.append([-z, -lit_a, lit_b]); clauses.append([-z, lit_a, -lit_b])
        clauses.append([z, lit_a, lit_b]); clauses.append([z, -lit_a, -lit_b])
        return z

    def AND2(name, x, y):                # z <=> x & y
        z = pool.id(name)
        clauses.append([-z, x]); clauses.append([-z, y]); clauses.append([z, -x, -y])
        return z

    def less_than(X, Y, i):
        """Return literal LT = [pos(X,i) < pos(Y,i)] and enforce pos(X,i)!=pos(Y,i)."""
        eqb = [EQ(('e', X, Y, i, b), A(X, i, b), A(Y, i, b)) for b in range(bb)]
        # tie_above[b] = all bits above b equal; tie_above[bb-1]=TRUE
        ta = [None]*bb; ta[bb-1] = TRUE
        for b in range(bb-2, -1, -1):
            ta[b] = AND2(('ta', X, Y, i, b), ta[b+1], eqb[b+1])
        # deciding-less at bit b: ta[b] & ~A_b & B_b
        dlt = []
        for b in range(bb):
            z = pool.id(('dl', X, Y, i, b))
            clauses.append([-z, ta[b]]); clauses.append([-z, -A(X, i, b)]); clauses.append([-z, A(Y, i, b)])
            clauses.append([z, -ta[b], A(X, i, b), -A(Y, i, b)])
            dlt.append(z)
        LT = pool.id(('LT', X, Y, i))
        clauses.append([-LT] + dlt)          # LT -> OR dlt
        for z in dlt: clauses.append([-z, LT])  # dlt -> LT
        # distinct: not all bits equal  ->  ~(ta[0] & eqb[0])
        clauses.append([-ta[0], -eqb[0]])
        return LT

    thr_strict = M//2 + 1
    thr_weak = M//2
    for X in range(n):
        for Y in range(X+1, n):
            lts = [less_than(X, Y, i) for i in range(M)]   # LT = X before Y (X beats Y) in band i
            # exactly one Paley arc among (X,Y): X->Y or Y->X
            if t[X][Y]:                       # X beats Y: count X-before-Y >= bound
                weak = covered is not None and ((covered[X] >> Y) & 1)
                bound = thr_weak if weak else thr_strict
                lits = lts
            else:                             # Y beats X: count Y-before-X = ~LT >= bound
                weak = covered is not None and ((covered[Y] >> X) & 1)
                bound = thr_weak if weak else thr_strict
                lits = [-l for l in lts]
            if bound >= 1:
                clauses.extend(CardEnc.atleast(lits=lits, bound=bound,
                                               encoding=EncType.totalizer, vpool=pool).clauses)
    return clauses, pool, A, n, bb


def decode_orders(model, A, n, M, bb):
    ms = set(model)
    orders = []
    for i in range(M):
        pos = []
        for X in range(n):
            v = sum((1 << b) for b in range(bb) if A(X, i, b) in ms)
            pos.append((v, X))
        # smaller position = earlier = top (higher value)
        orders.append([X for _, X in sorted(pos)])
    return orders


def verify(orders, p):
    import numpy as np
    R = len(orders); posm = np.zeros((R, p), dtype=np.int32)
    for r, row in enumerate(orders):
        for idx, v in enumerate(row): posm[r, v] = idx
    before = np.zeros((p, p), dtype=np.int32)
    for r in range(R):
        pr = posm[r]; before += (pr[:, None] < pr[None, :]).astype(np.int32)
    Q = {i*i % p for i in range(1, p)}
    paley = np.array([[1 if (j-i) % p in Q else 0 for j in range(p)] for i in range(p)], dtype=bool)
    mism = ties = 0
    for i in range(p):
        for j in range(p):
            if i == j: continue
            if 2*before[i, j] == R: ties += 1
            if bool(2*before[i, j] > R) != bool(paley[i, j]): mism += 1
    return mism, ties


def main():
    p = int(sys.argv[1]); M = int(sys.argv[2])
    solver = sys.argv[3] if len(sys.argv) > 3 else 'cadical300'
    budget = float(sys.argv[4]) if len(sys.argv) > 4 else 0
    t = qr_tournament(p)
    t0 = time.time()
    clauses, pool, A, n, bb = build_binary(t, M)
    print(f"[BIN {solver}] P_{p} M={M} bb={bb}: build {time.time()-t0:.1f}s clauses={len(clauses)} vars={pool.top}", flush=True)
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
    print(f"  solve {s.time():.1f}s result={res}", flush=True)
    if res is True:
        orders = decode_orders(s.get_model(), A, n, M, bb)
        mism, ties = verify(orders, p)
        print(f"  VERIFY (binary enc): valid={mism==0 and ties==0} (mism={mism}, ties={ties})", flush=True)
    s.delete()


if __name__ == "__main__":
    main()
