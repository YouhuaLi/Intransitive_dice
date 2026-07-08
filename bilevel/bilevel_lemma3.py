"""Bilevel decomposition using Erdos Lemma-3-style extraction: grow B small while
keeping A = common in-neighbours (beaters) large -> big sqrt(n) x log n bicliques.
Args: p [kmax] [seeds]"""
import sys, time
import numpy as np


def paley_out(p):
    Q = {i * i % p for i in range(1, p)}
    return [sum(1 << j for j in range(p) if i != j and (j - i) % p in Q) for i in range(p)]


def bits(m):
    while m:
        b = m & -m; yield b.bit_length() - 1; m ^= b


def extract(avail, rem_in, first_b, kmax):
    """Greedy Lemma-3 biclique from a seed 'first_b' (initial B member)."""
    B = 1 << first_b
    curA = rem_in[first_b] & avail & ~(1 << first_b)   # beaters of first_b
    bestA, bestB, bestprod = curA, B, curA.bit_count() * 1
    for _ in range(kmax - 1):
        # pick b (beaten by many of curA) maximizing |curA & rem_in[b]|
        cand = 0
        for a in bits(curA):
            cand |= 0  # placeholder
        # candidates: vertices in avail, not in B, beaten by >=1 of curA
        m = avail & ~B
        bestb = -1; bestov = 0
        while m:
            bit = m & -m; b = bit.bit_length() - 1; m ^= bit
            ov = (curA & rem_in[b]).bit_count()
            if ov > bestov:
                bestov = ov; bestb = b
        if bestb < 0 or bestov < 1:
            break
        newA = curA & rem_in[bestb] & ~(1 << bestb)
        if newA == 0:
            break
        B |= (1 << bestb); curA = newA
        prod = curA.bit_count() * B.bit_count()
        if prod > bestprod:
            bestprod = prod; bestA = curA; bestB = B
    return bestA, bestB


def decompose(p, kmax, seeds, maxlayers):
    out = paley_out(p)
    rem_out = out[:]; rem_in = [0] * p
    for i in range(p):
        for j in bits(out[i]):
            rem_in[j] |= (1 << i)
    ALL = (1 << p) - 1
    total = sum(x.bit_count() for x in rem_out)
    layers = []; covered = 0
    while covered < total and len(layers) < maxlayers:
        used = 0; blocks = []; avail = ALL
        while True:
            # seed candidates = available vertices that are still beaten (have in-edges) & beat something
            targets = [b for b in bits(avail) if rem_in[b] & avail]
            if not targets:
                break
            # try seeds: the most-beaten available vertices
            targets.sort(key=lambda b: -(rem_in[b] & avail).bit_count())
            trials = targets[:seeds]
            bestA = bestB = 0; bestprod = -1
            for fb in trials:
                A, B = extract(avail, rem_in, fb, kmax)
                pr = A.bit_count() * B.bit_count()
                if pr > bestprod:
                    bestprod = pr; bestA, bestB = A, B
            if bestprod <= 0:
                break
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
        for (A, B) in blocks: r1 += sorted(bits(A)) + sorted(bits(B))
        for (A, B) in reversed(blocks): r2 += sorted(bits(A), reverse=True) + sorted(bits(B), reverse=True)
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
    p = int(sys.argv[1])
    kmax = int(sys.argv[2]) if len(sys.argv) > 2 else max(4, int(2 * (p).bit_length()))
    seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    t0 = time.time()
    layers, total, covered = decompose(p, kmax, seeds, 10 * p); td = time.time() - t0
    t = len(layers)
    mism, ties, R = verify(layers, p)
    print(f"P({p}) kmax={kmax} seeds={seeds}: {t} layers -> {2*t} faces (2t-1={2*t-1})  "
          f"[{td:.1f}s]  valid={mism==0 and ties==0}", flush=True)


if __name__ == "__main__":
    main()
