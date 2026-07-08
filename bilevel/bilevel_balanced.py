"""Improved greedy bilevel decomposition: degree-based vertex selection inside
biclique growth (keep the most candidates), best-of-S seeds per biclique.
Args: p [seeds] [maxlayers]"""
import sys, time
import numpy as np


def paley_out(p):
    Q = {i * i % p for i in range(1, p)}
    return [sum(1 << j for j in range(p) if i != j and (j - i) % p in Q) for i in range(p)]


def bits(m):
    while m:
        b = m & -m; yield b.bit_length() - 1; m ^= b


def grow_biclique(u, v, avail, rem_out, rem_in):
    A = 1 << u; B = 1 << v
    candB = rem_out[u] & avail & ~(1 << v)
    candA = rem_in[v] & avail & ~(1 << u)
    while candA or candB:
        growA = (A.bit_count() <= B.bit_count() and candA) or not candB
        if growA:
            # pick w in candA maximizing overlap with candB (preserve most B-candidates)
            best = -1; bw = -1
            m = candA
            while m:
                b = m & -m; w = b.bit_length() - 1; m ^= b
                ov = (rem_out[w] & candB).bit_count()
                if ov > best: best = ov; bw = w
            A |= (1 << bw)
            candB &= rem_out[bw]; candA &= ~(1 << bw); candB &= ~(1 << bw)
        else:
            best = -1; bw = -1
            m = candB
            while m:
                b = m & -m; w = b.bit_length() - 1; m ^= b
                ov = (rem_in[w] & candA).bit_count()
                if ov > best: best = ov; bw = w
            B |= (1 << bw)
            candA &= rem_in[bw]; candA &= ~(1 << bw); candB &= ~(1 << bw)
    return A, B


def decompose(p, seeds, maxlayers):
    out = paley_out(p)
    rem_out = out[:]
    rem_in = [0] * p
    for i in range(p):
        for j in bits(out[i]):
            rem_in[j] |= (1 << i)
    ALL = (1 << p) - 1
    total = sum(x.bit_count() for x in rem_out)
    layers = []; covered = 0
    import random; random.seed(0)
    while covered < total and len(layers) < maxlayers:
        used = 0; blocks = []; avail = ALL
        while True:
            # collect available vertices with remaining out-edges
            srcs = [u for u in bits(avail) if rem_out[u] & avail]
            if not srcs:
                break
            # try several seeds, keep biggest biclique
            bestA = bestB = 0; bestsz = -1
            trials = srcs if len(srcs) <= seeds else random.sample(srcs, seeds)
            for u in trials:
                t = rem_out[u] & avail
                v = (t & -t).bit_length() - 1
                A, B = grow_biclique(u, v, avail, rem_out, rem_in)
                sz = A.bit_count() * B.bit_count()
                if sz > bestsz: bestsz = sz; bestA, bestB = A, B
            A, B = bestA, bestB
            blocks.append((A, B)); used |= A | B; avail = ALL & ~used
            for a in bits(A): rem_out[a] &= ~B
            for b in bits(B): rem_in[b] &= ~A
            covered += A.bit_count() * B.bit_count()
        for x in bits(ALL & ~used):
            blocks.append((1 << x, 0))
        layers.append(blocks)
    return layers, total, covered


def verify(layers, p):
    rows = []
    for blocks in layers:
        r1 = []; r2 = []
        for (A, B) in blocks:
            r1 += sorted(bits(A)) + sorted(bits(B))
        for (A, B) in reversed(blocks):
            r2 += sorted(bits(A), reverse=True) + sorted(bits(B), reverse=True)
        rows.append(r1); rows.append(r2)
    R = len(rows)
    pos = np.zeros((R, p), dtype=np.int32)
    for r, row in enumerate(rows):
        for idx, v in enumerate(row): pos[r, v] = idx
    before = np.zeros((p, p), dtype=np.int32)
    for r in range(R):
        pr = pos[r]; before += (pr[:, None] < pr[None, :]).astype(np.int32)
    Q = {i * i % p for i in range(1, p)}
    paley = np.array([[1 if (j - i) % p in Q else 0 for j in range(p)] for i in range(p)], dtype=bool)
    mism = ties = 0
    for i in range(p):
        for j in range(p):
            if i == j: continue
            if 2 * before[i, j] == R: ties += 1
            if bool(2 * before[i, j] > R) != bool(paley[i, j]): mism += 1
    return mism, ties, R


def main():
    p = int(sys.argv[1]); seeds = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    maxlayers = int(sys.argv[3]) if len(sys.argv) > 3 else 10 * p
    t0 = time.time()
    layers, total, covered = decompose(p, seeds, maxlayers); td = time.time() - t0
    t = len(layers)
    mism, ties, R = verify(layers, p)
    print(f"P({p}) seeds={seeds}: {t} layers -> {2*t} faces ({td:.1f}s)  mism={mism} ties={ties} valid={mism==0 and ties==0}", flush=True)


if __name__ == "__main__":
    main()
