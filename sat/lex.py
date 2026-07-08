"""Lexicographic <= constraint on two literal-vectors (index 0 = most significant).
Enforce A <=_lex B where A[k], B[k] are literals.  Run `python lex.py` to unit-test."""


def add_lex_leq(A, B, pool, clauses, tag):
    m = len(A)
    e_prev = pool.id('true')                       # equal-so-far before position 0 == TRUE
    for k in range(m):
        a, b = A[k], B[k]
        clauses.append([-e_prev, -a, b])           # equal so far -> not (a=1,b=0)
        if k == m - 1:
            break
        eq = pool.id(('lexeq', tag, k))            # eq <-> (a == b)
        clauses.append([-eq, -a, b])
        clauses.append([-eq, -b, a])
        clauses.append([-a, -b, eq])
        clauses.append([a, b, eq])
        e = pool.id(('lexe', tag, k))              # e <-> e_prev & eq
        clauses.append([-e, e_prev])
        clauses.append([-e, eq])
        clauses.append([-e_prev, -eq, e])
        e_prev = e


def _test():
    import itertools
    from pysat.formula import IDPool
    from pysat.solvers import Solver
    for m in range(1, 6):
        for va in itertools.product([0, 1], repeat=m):
            for vb in itertools.product([0, 1], repeat=m):
                pool = IDPool(); clauses = [[pool.id('true')]]
                A = []; B = []
                for k in range(m):
                    av = pool.id(('a', k)); bv = pool.id(('b', k))
                    A.append(av); B.append(bv)
                    clauses.append([av] if va[k] else [-av])
                    clauses.append([bv] if vb[k] else [-bv])
                add_lex_leq(A, B, pool, clauses, 't')
                s = Solver(name='minisat22', bootstrap_with=clauses)
                sat = s.solve(); s.delete()
                if sat != (list(va) <= list(vb)):
                    print(f"FAIL m={m} A={va} B={vb} sat={sat}"); return
    print("lex_leq unit test PASSED (all vectors up to len 5)")


if __name__ == "__main__":
    _test()
