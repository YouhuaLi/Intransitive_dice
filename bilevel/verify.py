"""Fast verify a dice file realizes Paley P(p): upper-triangle, numpy searchsorted."""
import sys, time
import numpy as np

fn = sys.argv[1]; p = int(sys.argv[2])
dice = [sorted(int(x) for x in l.split()) for l in open(fn) if l.strip()]
n = len(dice); d = len(dice[0])
arr = [np.array(x) for x in dice]
allv = np.concatenate(arr); nd = len(np.unique(allv))
print(f"n={n} d={d} total={n*d} distinct={nd} all-distinct={nd==n*d}", flush=True)
Q = {i * i % p for i in range(1, p)}
paley = lambda i, j: 1 if (j - i) % p in Q else 0
half = d * d / 2.0
mism = ties = 0
t0 = time.time()
for i in range(n):
    ai = arr[i]
    for j in range(i + 1, n):
        w = int(np.searchsorted(arr[j], ai, side='left').sum())
        if w == d * d - w: ties += 1
        if int(w > half) != paley(i, j): mism += 1
        if int((d * d - w) > half) != paley(j, i): mism += 1
print(f"DONE {time.time()-t0:.0f}s  tie pairs={ties}  mismatched ordered pairs={mism}", flush=True)
print(f"==> realizes Paley P({p}) no ties: {mism==0 and ties==0}", flush=True)
