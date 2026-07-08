# Bilevel construction for Paley intransitive dice

Realizes the Paley tournament `P(p)` (`p ≡ 3 mod 4` prime) as a majority of linear
orders (= dice faces), via the **bilevel edge-decomposition** of Erdős & Moser,
*On the representation of directed graphs as unions of orderings* (1964).

## Method

Partition the tournament's edges into `t` edge-disjoint **bilevel graphs** (each a
vertex-disjoint union of complete directed bicliques `A→B`). By Erdős–Moser Lemma 2,
each bilevel graph is realized by exactly **2 voters**, and every covered edge gets
majority margin **+2**. Stacking all layers → `2t` faces.

**Odd trim:** because every edge sits at margin +2, dropping *one* voter leaves all
margins in `{1,3} > 0`, so the tournament is preserved with **`2t − 1` faces** (odd,
matching the fact that minimum face counts are odd). Dropping two can create a tie.

Dice values are the banded reconstruction `face_r(v) = r·p + (p − pos_r(v))`, a
permutation of `1..p·d`; then die `i` beats die `j` (all-pairs majority) iff `i`
precedes `j` in a majority of voters — which equals `P(p)`.

## Files

| file | what |
|---|---|
| `bilevel_balanced.py` | **Best** decomposer: greedy, degree-based *balanced* biclique growth + multi-seed. `python bilevel_balanced.py <p> [seeds]` |
| `bilevel_naive.py` | Baseline greedy (lowest-bit growth). Weaker. |
| `bilevel_lemma3.py` | Erdős Lemma-3-style `√n × log n` asymmetric extraction. **Worse in practice** (asymmetric bicliques waste vertices → more layers). |
| `gen_dice.py` | Produce a verified odd-face dice file: `python gen_dice.py <p> [seeds] [outdir]` |
| `verify.py` | Independent verifier: `python verify.py <dicefile> <p>` |

## Results (verified: 0 ties, values a permutation of 1..p·d, all ordered pairs match P(p))

| p | bilevel faces (2t−1) | 2t/p | best other known | note |
|---|---|---|---|---|
| 67 | 57 | 0.87 | **17** (SAT) | bilevel loses badly for small p |
| 331 | 179 | 0.54 | **167** (newbednay ≈(p+1)/2) | bilevel loses (below crossover) |
| 503 | 257 | 0.51 | **252** (newbednay ≈(p+1)/2) | bilevel loses (below crossover) |
| **523** | **261** | 0.50 | 262 (newbednay ≈(p+1)/2) | **crossover — bilevel WINS by 1** → `../paley523_261face.txt` |
| 743 | **349** | 0.47 | 371 (chain), ≈372 (newbednay) | **bilevel WINS (beats even chain)** → `../paley743_349face.txt` |
| 991 | **445** | 0.45 | 495 (chain), ≈496 (newbednay) | **bilevel WINS (beats even chain)** → `../paley991_445face.txt` |
| 1163 | **519** | 0.45 | 583 (newbednay) | **bilevel WINS (−11%)** → `../paley1163_519face.txt` |

## When is bilevel worth it?

- **Small p:** lose to SAT (rank encoding, `../FACE_COUNTS.md`).
- **Mid p (up to ≈500):** lose to the `≈(p+1)/2` "newbednay" construction.
- **Large p (≈520+):** bilevel's ratio `2t/p ≈ C/ln p` (C≈3.2, i.e. `Θ(p/log p)`) drops
  below `(p+1)/(2p) ≈ 0.5` and it wins. **Crossover is p≈523** (verified: 261 < 262), NOT
  ~1000 — newbednay's effective constant `0.5·ln p` grows while bilevel's C≈3.2 is flat,
  so they cross at `ln p ≈ 6.4`. Wins confirmed at p = 523, 743, 991, 1163; at 743/991
  (≡7 mod 8) bilevel even beats the chain `(p−1)/2`.
- Extrapolation: bilevel only undercuts the conjectured minimum `(p+1)/4` at
  **p ≈ 10⁵–3×10⁵** (this greedy); an optimal decomposition would cross earlier.
  For all computationally testable p, `(p+1)/4` remains unbeaten by any construction.
