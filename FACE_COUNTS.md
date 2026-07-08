# Face counts for Paley intransitive dice

How few faces are needed to realize the Paley tournament `P(p)` (`p ≡ 3 mod 4`,
a prime) as an intransitive dice set — i.e. as the **majority of F linear orders**,
one face per order. `F` = number of faces per die.

Realizing `P(p)` makes the dice `(k+1)`-player intransitive, where `k` is the
largest Schütte index with `γ(P(p)) ≥ k+1` (see OEIS A362137). Here we only track
the **face count**, not the player count.

## Two deterministic constructions

| Construction | Faces | Works for | Notes |
|---|---|---|---|
| **Chain** (Bednay–Bozóki "Construction 7") | **(p−1)/2** | **p ≡ 7 (mod 8)** only | closed form, instant, no search |
| **Construction 6** (Bednay–Bozóki 2013) | **p** | **all p ≡ 3 (mod 4)** | closed form, instant, no search; each die has equal face-sum |

- **Construction 6** is the universal fallback: it always gives `p` faces for any Paley prime.
- The **chain** halves that to `(p−1)/2` whenever `p ≡ 7 (mod 8)`.

Both are implemented in `gen_unified.py` (default = Construction 6; `--chain` = chain).

## Classification by prime

| p | p mod 8 | **known min faces** | comment |
|---|---|---|---|
| 7 | 7 | **3** | chain = (p−1)/2 = 3; also = (p+1)/4; minimality not SAT-checked |
| 11 | 3 | **5** | SAT §; **proven minimal** (d = 3,4 UNSAT); formula's lone exception (>3) |
| 19 | 3 | **5** | SAT ◆; **proven minimal** (d = 3,4 UNSAT); = (p+1)/4 — 1st non-exception exact confirmation |
| 23 | 7 | **7** | SAT ◆; = (p+1)/4; below chain's 11; not proven minimal |
| 31 | 7 | **9** | SAT ◆; = (p+1)/4; below chain's 15; not proven minimal |
| 43 | 3 | **11** | SAT ¶ (`paley43_11face.txt`); = (p+1)/4; not proven minimal |
| 47 | 7 | **13** | SAT ◆ (`paley47_13face.txt`); = (p+1)/4; below chain's 23; not proven minimal |
| 59 | 3 | **15** | SAT ◆ (`paley59_15face.txt`); = (p+1)/4; beats literature's 29; not proven minimal |
| 67 | 3 | **17** | SAT ‡◆ (`paley67_17face.txt`); = (p+1)/4; **d = 15 under test**; not proven minimal |
| 71 | 7 | **19** | SAT ◆ (`paley71_19face.txt`); = (p+1)/4; below chain's 35; not proven minimal |
| 79 | 7 | **39** | chain construction only; **no SAT run**; formula conjectures 21 (untested) |
| 83 | 3 | **83** | Constr. 6 (p faces) only; **no SAT run**; formula conjectures 21 (untested) |
| 103 | 7 | **45** | residual-SAT hybrid ✚ (`sat/paley103_45face_hybrid.txt`, K=14 bilevel head + M=17 SAT); **beats chain's 51**; formula conjectures 27; sub-45 timed out at 240s |
| 331 | 3 | **167** | "newbednay" construction (`best_results/p_331_f_167_newbednay.txt`, ≈(p+1)/2); bilevel ✦ only reaches 179 here (below crossover); formula conjectures 83 |
| 523 | 3 | **261** | bilevel ✦ (`paley523_261face.txt`); **crossover** — first prime bilevel beats newbednay's (p+1)/2 = 262 (and Construction 6's 523); formula conjectures 131 |
| 743 | 7 | **349** | bilevel ✦ (`paley743_349face.txt`); **beats even the chain 371** and newbednay's ≈372; formula conjectures 187 |
| 991 | 7 | **445** | bilevel ✦ (`paley991_445face.txt`); **beats even the chain 495** and newbednay's ≈496; formula conjectures 249 |
| 1163 | 3 | **519** | bilevel (Erdős–Moser) ✦ (`paley1163_519face.txt`); **beats** the newbednay 583; formula conjectures 291 |

\* Bednay & Bozóki (2013) report a `(p−1)/2` realization for **11, 19, 59**
specifically; a general construction for `p ≡ 3 (mod 8)` is **open**. Our
annealing (`gen_9face_4player.py` / the `--reduce` mode of `gen_unified.py`)
independently reproduced **11 and 19**, but not 59.

‡ **p = 67, 17 faces (SAT).** A SAT encoding (repo `nontransitive-dice-SteefCoder`,
CaDiCaL 3.0 with **column-permutation symmetry breaking**) found a **17-face**
realization of `P(67)` (`paley67_17face.txt`, ~7.9 h) — matching the conjectured
`(p+1)/4 = 17`, well below `(p−1)/2 = 33` and Construction 6's 67. Verified
independently: 0 tied pairs and all `67·66 = 4422` ordered pairs match `P(67)`.
(An earlier 19-face solution, `paley67_19face.txt`, found in ~2 h, still stands as
a slack witness.) Not claimed minimal, but it completes the 8/8 agreement with the
`(p+1)/4` formula and shows the true minimum falls **far below** the `(p−1)/2`
construction target.

§ **p = 11, minimum = 5 (proven).** The same SAT encoding proves `d = 3` and
`d = 4` are both **UNSAT** and `d = 5` is SAT (verified) — so **5 is the exact
minimum** face count for `P(11)`, a genuine lower bound rather than merely the
best construction (`paley11_5face.txt`, an all-margin-±1 realization: every pair
decided 3:2). (This matches Gogoi 2026's non-affine minimum of 5.) For
larger `p` the SAT *upper* bounds are reachable (e.g. 19 for `P(67)`) but the
matching UNSAT *lower* bounds blow up, so optimality is settled only for the
small primes.

¶ **p = 43, 11 faces (SAT).** Same method (CaDiCaL + column-permutation symmetry
breaking) realizes `P(43)` in **11 faces** — about half of `(p−1)/2 = 21`, and far
under Construction 6's 43. Verified: 0 ties, all `43·42 = 1806` ordered pairs match
`P(43)` (`paley43_11face.txt`). Found quickly (`d = 13` in ~15 s, `d = 11` in ~21 min);
lower values (`d = 9, 7`) did not resolve within an hour and were not pushed further,
so 11 is the best found, **not** claimed minimal.

◆ **SAT face counts and a conjecture.** Using the SAT encoding + column-permutation
symmetry breaking (all solutions verified: 0 ties, values a permutation of `1..p·d`,
each ordered pair matching `P(p)`; files `paley<p>_<d>face.txt`), the minimum face
counts found so far are:

| p | 19 | 23 | 31 | 43 | 47 | 59 | 67 | 71 |
|---|----|----|----|----|----|----|----|----|
| **SAT faces** | 5 | 7 | 9 | 11 | 13 | 15 | 17 | 19 |
| **least odd ≥ (p+1)/4** | 5 | 7 | 9 | 11 | 13 | 15 | 17 | 19 |

Every determined value equals **the smallest odd integer ≥ `(p+1)/4`** (**8/8** for
p = 19…71, all verified). This is ≈ `p/4` — roughly **half** the `(p−1)/2` constructions, and it beats
the literature for 59 (29→15) and the chain for 47/71 (23→13, 35→19). `p = 11` is the
lone exception (formula → 3, true min = 5, proven §). These are verified **upper
bounds**; optimality is proven only for `p = 11`. The odd-parity of every entry is
forced (majority rule admits no ties). Whether the formula is exact for all `p > 11`
is **open** — the tractable half is a general `≈(p+1)/4`-face construction; a matching
lower bound (spectral, via `|λ| = √p` of the Paley matrix) is harder.

✦ **Bilevel construction (Erdős–Moser 1964), for large p where SAT is infeasible.**
Decompose the tournament's edges into `t` edge-disjoint *bilevel* graphs (each a
vertex-disjoint union of complete directed bicliques); by their Lemma 2 each bilevel
graph is realized by exactly **2 voters**, giving `2t` faces with every edge at margin
`+2`. Because of that `+2` slack, **dropping any one voter keeps all margins in {1,3}>0**,
so the cost is really **`2t − 1`** (odd — consistent with minima being odd). A greedy
decomposer (`scratchpad/bilevel2.py`, degree-based biclique growth + multi-seed) gives,
verified (0 ties, values a permutation of `1..p·d`, all ordered pairs match Paley):
`P(331) → 183` (`paley331_183face.txt`) and `P(1163) → 519` (`paley1163_519face.txt`).
The ratio `2t/p` falls with `p` (≈0.56 at 331, ≈0.45 at 1163), matching the theorem's
`Θ(p/log p)`. **It overtakes the author's ≈(p+1)/2 "newbednay" construction from `p ≈ 523`**
(corrected 2026-07-07 — the earlier "~1000" estimate was wrong). Newbednay's effective
constant `((p+1)/2)/p·ln p ≈ 0.5·ln p` *grows* with p while bilevel's `2t/p·ln p = C ≈ 3.2`
is roughly flat (measured 3.51→3.18 over p=67…523), so they cross at `ln p ≈ 6.4`, i.e.
`p ≈ 520`. Verified crossover: `2t−1` first drops below `(p+1)/2` at **p = 523 (261 < 262)**
(`paley523_261face.txt`); further wins at **p = 743 (349 vs 372)** and **p = 991 (445 vs
496)** (`paley743_349face.txt`, `paley991_445face.txt`), then **p = 1163 (519 vs 583)** —
all 0 ties, all ordered pairs match P(p). Below the crossover it loses: **p = 331 (best 179
vs newbednay's 167)** and **p = 503 (257 vs 252)**. It also loses to SAT for small p (p=67:
57 vs 17), and stays well above the conjectured `(p+1)/4` (that crossover is far out,
`p ≈ 10⁵–3×10⁵`) — it is a restricted edge-disjoint, margin-±{1,3} scheme. The greedy is
near its own ceiling (best-of-restarts barely moves p=331: 90 layers), so a smarter biclique
finder would be needed to push lower or to beat newbednay below p≈520.

✚ **Residual-SAT hybrid (2026-07-07).** For mid-size p where pure SAT is infeasible but the
chain/Construction-6 are far from optimal: use a bilevel *head* (first `K` layers = `2K`
voters, each covered arc at margin +2) then `M` SAT voters for the sparse residual, total
`2K+M` (odd). Because covered arcs keep their +2, they need only a *weak* SAT bound
(`c ≥ ⌊M/2⌋`) vs the residual's strict majority (`c ≥ ⌊M/2⌋+1`), so M can be small. **Key
implementation gotcha: run SAT with symmetry breaking OFF** — SB slows *finding* a solution
(p=103 K=20 M=9: >8 min with SB, 7.8 s without — but that speed is the hybrid's *slack*, not
SB-off in general: pure SAT stays hard, e.g. SB-off didn't find the known P(67) d=17 in 15 min).
Best result: **P(103) in 45 faces** (`sat/paley103_45face_hybrid.txt`, K=14 head + M=17 SAT,
verified 0 ties), **below the chain's `(p−1)/2 = 51`**. Tool: `sat/hybrid.py`. p=331 is
memory-unsafe for SAT (`n³·M` ≈ 8.6 GB even at M=3). Pushing p=103 below 45 and extending to
p = 127 (chain 63) is open — see `RESEARCH_LOG.md`.

## The three categories

**① Deterministic → (p−1)/2 faces** — exactly the primes **p ≡ 7 (mod 8)**:
`7, 23, 31, 47, 71, 79, 103, 127, 151, …` (chain / Construction 7).

**② Deterministic → p faces** — **every** Paley prime `p ≡ 3 (mod 4)` (Construction 6).
This is the fallback for the `p ≡ 3 (mod 8)` primes where the chain fails:
`11, 19, 43, 59, 67, 83, …`

**③ Annealing reached (p−1)/2 where no deterministic (p−1)/2 exists** (i.e. `p ≡ 3 mod 8`):
only the small ones — **p = 11 (5 faces)** and **p = 19 (9 faces)**. Beyond that
(43, 59, 67, …) the simulated-annealing *stalls* within minutes — but a **SAT
solver with column-permutation symmetry breaking** does not: it reaches
**11 faces for p = 43** (¶) and **19 faces for p = 67** (‡), both well *below*
`(p−1)/2` (21 and 33). So the stall is a limitation of annealing, not evidence
that `(p−1)/2` is near-optimal.

## Takeaways

- **p ≡ 7 (mod 8):** use the chain → `(p−1)/2` faces, deterministic, done.
- **p ≡ 3 (mod 8), small (11, 19):** annealing reaches the `(p−1)/2` optimum;
  59 is known in the literature but our search doesn't reach it.
- **p ≡ 3 (mod 8), larger (43, 59, 67, 83, …):** no *deterministic* sub-`p`
  construction, and annealing stalls — but a **SAT solver** cracks them:
  `P(43)` → **11 faces** (¶) and `P(67)` → **19 faces** (‡), far under both
  Construction 6 and `(p−1)/2`. Extending this SAT approach to 59, 83, … is the
  natural next step.
- **Practical consequence:** for `P(67)` you are no longer stuck at 67 faces —
  the SAT set gives **19 faces** directly (`paley67_19face.txt`). Switching to
  `p = 71` (`≡ 7 mod 8`) → 35 faces via the chain is now only attractive if you
  specifically need the closed-form/deterministic guarantee rather than the
  smallest face count.

## Notes / caveats

- The minimum face count `F` for a specific tournament is its *representation
  number* / *majority dimension* (McGarvey; Alon 2002). Worst case over all
  n-vertex tournaments is `Θ(n / log n)`; for Paley `P(p)` the exact minimum is
  generally not known in closed form.
- No **minimality** is claimed for the `(p−1)/2` counts above (they are the
  *best construction we have*, not proven lower bounds) — **except `p = 11`,
  where a SAT solver proves the minimum is exactly 5** (§). (Gogoi 2026 shows the
  minimum over *affine* voters for `P(11)` is 7, while non-affine gives 5 —
  matching the SAT bound — so the true minimum can be below `(p−1)/2`.)

### References
- D. Bednay, S. Bozóki, *Constructions for nontransitive dice sets*, Proc. 8th
  Japanese–Hungarian Symposium on Discrete Math. (2013), 15–23. (Constructions 6 & 7.)
- S. Bozóki, *Nontransitive dice sets realizing the Paley tournaments*, Miskolc
  Math. Notes 15 (2014), 39–50. (`p(p−1)/2`-face set `D_p`.)
- N. Alon, *Voting paradoxes and digraphs realizations*, Adv. Appl. Math. 29 (2002).
- A. Gogoi, *Condorcet's Paradox in Finite Fields: Constructing Paley Tournaments
  with Minimal Voter*, SSRN (2026). (Exact backtracking over affine voters.)
