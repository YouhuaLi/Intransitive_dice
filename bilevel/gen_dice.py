"""Generate a verified Paley P(p) dice set via the balanced bilevel decomposition,
trimmed to an ODD face count (2t-1).  Writes paley<p>_<d>face.txt.
Usage:  python gen_dice.py <p> [seeds] [outdir]
Run from this directory (imports bilevel_balanced)."""
import sys
import numpy as np
from bilevel_balanced import decompose, bits


def main():
    p = int(sys.argv[1])
    seeds = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    outdir = sys.argv[3] if len(sys.argv) > 3 else "."
    layers, total, covered = decompose(p, seeds, 10 * p)
    rows = []
    for blocks in layers:
        r1 = []; r2 = []
        for (A, B) in blocks:
            r1 += sorted(bits(A)) + sorted(bits(B))
        for (A, B) in reversed(blocks):
            r2 += sorted(bits(A), reverse=True) + sorted(bits(B), reverse=True)
        rows.append(r1); rows.append(r2)
    rows = rows[:-1]                                  # drop one voter -> odd (margins stay in {1,3})
    m = len(rows)
    dice = [[] for _ in range(p)]
    for r, row in enumerate(rows):
        for idx, v in enumerate(row):
            dice[v].append(r * p + (p - idx))          # banded: earlier position -> higher value
    dice = [sorted(d) for d in dice]

    # verify
    arr = [np.array(x) for x in dice]
    Q = {i * i % p for i in range(1, p)}
    paley = lambda i, j: 1 if (j - i) % p in Q else 0
    half = m * m / 2.0
    mism = ties = 0
    for i in range(p):
        for j in range(i + 1, p):
            w = int(np.searchsorted(arr[j], arr[i], side='left').sum())
            if w == m * m - w: ties += 1
            if int(w > half) != paley(i, j): mism += 1
            if int((m * m - w) > half) != paley(j, i): mism += 1
    ok = (mism == 0 and ties == 0)
    fn = f"{outdir}/paley{p}_{m}face.txt"
    if ok:
        with open(fn, "w") as f:
            for d in dice:
                f.write(" ".join(map(str, d)) + "\n")
    print(f"P({p}): {len(layers)} bilevel layers -> {m} faces (2t-1); "
          f"verified={ok} (mism={mism}, ties={ties}); {'wrote '+fn if ok else 'NOT written'}")


if __name__ == "__main__":
    main()
