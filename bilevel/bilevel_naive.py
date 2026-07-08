"""Greedy bilevel edge-decomposition of the Paley tournament P(p) (Erdos-Moser).
Each bilevel layer = 2 voters; face count = 2 * (#layers).  Builds the R-matrix
per Lemma 2 and VERIFIES majority == Paley.  Args: p [maxlayers]
"""
import sys, time
import numpy as np


def paley_out(p):
    Q = {i * i % p for i in range(1, p)}
    out = [0] * p
    for i in range(p):
        m = 0
        for j in range(p):
            if i != j and (j - i) % p in Q:
                m |= (1 << j)
        out[i] = m
    return out


def bits(m):
    while m:
        b = m & -m
        yield b.bit_length() - 1
        m ^= b


def decompose(p, maxlayers):
    out = paley_out(p)
    rem_out = out[:]                      # remaining out-edges (uncovered)
    rem_in = [0] * p
    for i in range(p):
        mm = out[i]
        while mm:
            b = mm & -mm; j = b.bit_length() - 1; mm ^= b
            rem_in[j] |= (1 << i)
    ALL = (1 << p) - 1
    total = sum(x.bit_count() for x in rem_out)
    layers = []
    covered = 0
    while covered < total and len(layers) < maxlayers:
        used = 0
        blocks = []
        avail = ALL
        while True:
            # seed: a remaining edge among available vertices
            seed = None
            am = avail
            while am:
                b = am & -am; u = b.bit_length() - 1; am ^= b
                t = rem_out[u] & avail
                if t:
                    v = (t & -t).bit_length() - 1
                    seed = (u, v); break
            if seed is None:
                break
            u, v = seed
            A = 1 << u; B = 1 << v
            candB = rem_out[u] & avail & ~(1 << v)
            candA = rem_in[v] & avail & ~(1 << u)
            while candA or candB:
                growA = (A.bit_count() <= B.bit_count() and candA) or not candB
                if growA:
                    w = (candA & -candA).bit_length() - 1
                    A |= (1 << w)
                    candB &= rem_out[w]
                    candA &= ~(1 << w); candB &= ~(1 << w)
                else:
                    w = (candB & -candB).bit_length() - 1
                    B |= (1 << w)
                    candA &= rem_in[w]
                    candA &= ~(1 << w); candB &= ~(1 << w)
            blocks.append((A, B))
            used |= A | B
            avail = ALL & ~used
            # remove covered edges A->B
            for a in bits(A):
                rem_out[a] &= ~B
            for b in bits(B):
                rem_in[b] &= ~A
            covered += A.bit_count() * B.bit_count()
        # leftover vertices -> singleton blocks (cancel with everything)
        for x in bits(ALL & ~used):
            blocks.append((1 << x, 0))
        layers.append(blocks)
    return layers, total, covered


def build_rows(layers, p):
    rows = []
    for blocks in layers:
        r1 = []; r2 = []
        for (A, B) in blocks:
            a = sorted(bits(A)); b = sorted(bits(B))
            r1 += a + b
        for (A, B) in reversed(blocks):
            a = sorted(bits(A), reverse=True); b = sorted(bits(B), reverse=True)
            r2 += a + b
        rows.append(r1); rows.append(r2)
    return rows


def verify(rows, p):
    R = len(rows)
    pos = np.zeros((R, p), dtype=np.int32)
    for r, row in enumerate(rows):
        for idx, v in enumerate(row):
            pos[r, v] = idx
    before = np.zeros((p, p), dtype=np.int32)
    for r in range(R):
        pr = pos[r]
        before += (pr[:, None] < pr[None, :]).astype(np.int32)
    beats = (2 * before > R)
    Q = {i * i % p for i in range(1, p)}
    paley = np.array([[1 if (j - i) % p in Q else 0 for j in range(p)] for i in range(p)], dtype=bool)
    mism = 0; ties = 0
    for i in range(p):
        for j in range(p):
            if i == j: continue
            if 2 * before[i, j] == R: ties += 1
            if bool(beats[i, j]) != bool(paley[i, j]): mism += 1
    return mism, ties, R


def main():
    p = int(sys.argv[1]); maxlayers = int(sys.argv[2]) if len(sys.argv) > 2 else 10 * int(sys.argv[1])
    t0 = time.time()
    layers, total, covered = decompose(p, maxlayers)
    td = time.time() - t0
    t = len(layers)
    print(f"P({p}): {t} bilevel layers -> {2*t} faces  (edges {covered}/{total}, {td:.1f}s)", flush=True)
    rows = build_rows(layers, p)
    mism, ties, R = verify(rows, p)
    print(f"  R-matrix rows={R}  mismatches={mism}  ties={ties}  realizes P({p}): {mism==0 and ties==0}", flush=True)


if __name__ == "__main__":
    main()
