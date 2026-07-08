"""SAT with FULL Paley-automorphism symmetry breaking — for lower-bound / UNSAT attacks.

Adds lex-leader constraints x <=_lex sigma(x) for every non-identity automorphism of P(p)
(row maps x -> a*x+b with a a quadratic residue; group order p*(p-1)/2) PLUS adjacent
column transpositions.  Sound for any collection of symmetries (the global lex-min of the
group satisfies all of them).  This is far stronger pruning than plain column SB and is the
tool of choice for proving small-d UNSAT (e.g. establishing minimality).

Usage:  python sat_paley_sb.py <p> <d> [solver]

Validate soundness on a known-SAT instance before trusting an UNSAT result (a known-SAT
case must stay SAT).  Self-contained.
"""
import sys, os, time, gc
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver
from lex import add_lex_leq


def qr_tournament(p):
    Q = {i * i % p for i in range(1, p)}
    return [[1 if (j - i) % p in Q else 0 for j in range(p)] for i in range(p)]


def bits(m):
    while m:
        b = m & -m; yield b.bit_length() - 1; m ^= b


def build(t, d, p):
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
    # symmetry breaking: fixed var order over (X<Y, i)
    triples = [(X, Y, i) for X in range(n) for Y in range(X + 1, n) for i in range(d)]
    A = [V(X, Y, i, i) for (X, Y, i) in triples]
    QR = {a * a % p for a in range(1, p)}
    nsb = 0
    for a in sorted(QR):
        for b in range(p):
            if a == 1 and b == 0: continue
            sig = [(a * x + b) % p for x in range(p)]         # die x -> die sig[x]
            B = [V(sig[X], sig[Y], i, i) for (X, Y, i) in triples]
            add_lex_leq(A, B, pool, clauses, ('row', a, b)); nsb += 1
    for i0 in range(d - 1):
        sw = {i0: i0 + 1, i0 + 1: i0}
        B = [V(X, Y, sw.get(i, i), sw.get(i, i)) for (X, Y, i) in triples]
        add_lex_leq(A, B, pool, clauses, ('col', i0)); nsb += 1
    return clauses, pool, V, n, nsb


def reconstruct(model, V, n, d):
    ms = set(model)
    return [sorted(sum(1 for Y in range(n) for j in range(d) if V(X, Y, i, j) in ms)
                   for i in range(d)) for X in range(n)]


def main():
    p = int(sys.argv[1]); d = int(sys.argv[2])
    solver = sys.argv[3] if len(sys.argv) > 3 else 'cadical300'
    t = qr_tournament(p)
    print(f"[{solver}] P_{p} d={d} FULL-PALEY-SB", flush=True)
    t0 = time.time()
    clauses, pool, V, n, nsb = build(t, d, p)
    print(f"  build {time.time()-t0:.1f}s clauses={len(clauses)} vars={pool.top} ({nsb} syms)", flush=True)
    s = Solver(name=solver, bootstrap_with=clauses); del clauses; gc.collect()
    res = s.solve()
    print(f"  result={res}", flush=True)
    if res:
        dice = reconstruct(s.get_model(), V, n, d)
        ok = all((sum(1 for a in dice[i] for b in dice[j] if a > b) * 2 > d * d) == bool(t[i][j])
                 for i in range(n) for j in range(n) if i != j)
        print(f"  SAT verified={ok}", flush=True)
    else:
        print(f"  UNSAT at d={d}  => P({p}) needs > {d} faces", flush=True)
    s.delete()


if __name__ == "__main__":
    main()
