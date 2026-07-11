"""Hybrid with the COMPACT BINARY encoding: bilevel head (2K voters, covered arcs +2)
+ M SAT voters (binary-position encoding, memory ~O(n^2 M log n)). Enables large p.
Usage: python hybrid_bin.py <p> <K> <M> [solver] [budget_s]"""
import sys, os, time, gc, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from pysat.solvers import Solver
from hybrid import head_orders, qr_tournament, verify_full
from sat_bin import build_binary, decode_orders


def main():
    p = int(sys.argv[1]); K = int(sys.argv[2]); M = int(sys.argv[3])
    solver = sys.argv[4] if len(sys.argv) > 4 else 'cadical300'
    budget = float(sys.argv[5]) if len(sys.argv) > 5 else 0
    t = qr_tournament(p)
    t0 = time.time()
    orders, covered, R = head_orders(p, K)
    ncov = sum(c.bit_count() for c in covered); narcs = sum(sum(r) for r in t)
    print(f"P({p}) K={K} -> {R} head voters; covered {ncov}/{narcs}; residual {narcs-ncov} "
          f"({(narcs-ncov)/narcs*100:.1f}%)  M={M}  total faces={R+M}", flush=True)
    clauses, pool, A, n, bb = build_binary(t, M, covered)
    print(f"  BIN build {time.time()-t0:.1f}s clauses={len(clauses)} vars={pool.top} bb={bb}", flush=True)
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
        sat_ord = decode_orders(s.get_model(), A, n, M, bb)
        allo = orders + sat_ord
        mism, ties, Rf = verify_full(allo, p)
        ok = (mism == 0 and ties == 0)
        print(f"  COMBINED {Rf} faces: valid={ok} (mism={mism}, ties={ties})", flush=True)
        if ok:
            dice = [[] for _ in range(p)]
            for r, row in enumerate(allo):
                for idx, v in enumerate(row): dice[v].append(r*p + (p-idx))
            dice = [sorted(d) for d in dice]
            fn = f"paley{p}_{Rf}face_hybridbin.txt"
            with open(fn, "w") as f:
                for d in dice: f.write(" ".join(map(str, d)) + "\n")
            print(f"  wrote {fn}", flush=True)
    s.delete()


if __name__ == "__main__":
    main()
