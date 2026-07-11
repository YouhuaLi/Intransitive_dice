# Face counts for Paley intransitive dice

How few faces are needed to realize the Paley tournament `P(p)` (`p ≡ 3 mod 4`,
a prime) as an intransitive dice set — i.e. as the **majority of F linear orders**,
one face per order. `F` = number of faces per die.

Realizing `P(p)` makes the dice `(k+1)`-player intransitive, where `k` is the
largest Schütte index with `γ(P(p)) ≥ k+1` (see OEIS A362137). Here we only track
the **face count**, not the player count.

## Deterministic constructions

| Construction | Faces | Works for | Notes |
|---|---|---|---|
| **Chain** (Bednay–Bozóki "Construction 7") | **(p−1)/2** | **p ≡ 7 (mod 8)** only | closed form, instant, no search |
| **Construction 6** (Bednay–Bozóki 2013) | **p** | **all p ≡ 3 (mod 4)** | closed form, instant, no search; each die has equal face-sum |
| **newbednay** (`bb_direct.build_paley_3mod8`) | **(p+3)/2** | **p ≡ 3 (mod 8)** | closed form (scan `c`); realizes `P(p)` exactly |
| **newbednay − 2 voters** ★ | **(p−1)/2** | **p ≡ 3 (mod 8), except Heegner 67 & 163** | drop 2 redundant voters (0-flip); tournament unchanged |

- **Construction 6** is the universal fallback: it always gives `p` faces for any Paley prime.
- The **chain** halves that to `(p−1)/2` whenever `p ≡ 7 (mod 8)`.
- **newbednay** (sibling repo's `n-player/bb_direct.py`) covers the `p ≡ 3 (mod 8)`
  primes the chain misses, at `(p+3)/2` faces (`(p+1)/2` itself is even → ties).
- **★ newbednay − 2 voters** (2026-07-10): for `p ≡ 3 (mod 8)` the newbednay set
  contains **2 redundant voters** — a degenerate voter (column `k=(p−1)/2`) plus one
  of its `(p+1)/4` "0-flip" partners can be deleted, flipping **no** edges, so the
  tournament is preserved exactly and faces drop to **`(p−1)/2`** (matching the chain's
  count for `p ≡ 7 (mod 8)`, far below Construction 6's `p`). This **fails only for the
  two Heegner primes `≡ 3 (mod 8)`, `p = 67` and `p = 163`** (see ★ below), which stay
  at `(p+3)/2`.

Chain and Construction 6 are in `gen_unified.py` (default = Construction 6; `--chain` = chain).

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
| 67 | 3 | **17** | SAT ‡◆ (`paley67_17face.txt`); = (p+1)/4; **d = 15 under test**; not proven minimal. ★ Heegner: newbednay's 35 is **not** reducible |
| 71 | 7 | **19** | SAT ◆ (`paley71_19face.txt`); = (p+1)/4; below chain's 35; not proven minimal |
| 79 | 7 | **39** | chain construction only; **no SAT run**; formula conjectures 21 (untested) |
| 83 | 3 | **41** | newbednay − 2 voters ★ (`paley83_41face.txt`) = (p−1)/2; beats Constr. 6's 83; formula conjectures 21 |
| 103 | 7 | **45** | residual-SAT hybrid ✚ (`sat/paley103_45face_hybrid.txt`, K=14 bilevel head + M=17 SAT); **beats chain's 51**; formula conjectures 27; sub-45 timed out at 240s |
| 107 | 3 | **53** | newbednay − 2 voters ★ (`paley107_53face.txt`) = (p−1)/2; beats Constr. 6's 107; formula conjectures 27 |
| 131 | 3 | **65** | newbednay − 2 voters ★ (`paley131_65face.txt`) = (p−1)/2; beats Constr. 6's 131; formula conjectures 33 |
| 139 | 3 | **69** | newbednay − 2 voters ★ (`paley139_69face.txt`) = (p−1)/2; beats Constr. 6's 139; formula conjectures 35 |
| 163 | 3 | **83** | newbednay ★ (`(p+3)/2`); Heegner: **not** reducible to (p−1)/2=81; beats Constr. 6's 163; formula conjectures 41 |
| 179 | 3 | **89** | newbednay − 2 voters ★ (`paley179_89face.txt`) = (p−1)/2; beats Constr. 6's 179; formula conjectures 45 |
| 211 | 3 | **105** | newbednay − 2 voters ★ (`paley211_105face.txt`) = (p−1)/2; beats Constr. 6's 211; formula conjectures 53 |
| 227 | 3 | **113** | newbednay − 2 voters ★ (`paley227_113face.txt`) = (p−1)/2; beats Constr. 6's 227; formula conjectures 57 |
| 251 | 3 | **125** | newbednay − 2 voters ★ (`paley251_125face.txt`) = (p−1)/2; beats Constr. 6's 251; formula conjectures 63 |
| 283 | 3 | **141** | newbednay − 2 voters ★ (`paley283_141face.txt`) = (p−1)/2; beats Constr. 6's 283; formula conjectures 71 |
| 307 | 3 | **153** | newbednay − 2 voters ★ (`paley307_153face.txt`) = (p−1)/2; beats Constr. 6's 307; formula conjectures 77 |
| 331 | 3 | **165** | newbednay − 2 voters ★ (`paley331_165face.txt`) = (p−1)/2; was 167 (`p_331_f_167_newbednay.txt`); bilevel ✦ reaches only 179; formula conjectures 83 |
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

★ **newbednay − 2 voters → `(p−1)/2` for `p ≡ 3 (mod 8)`; Heegner exceptions 67 & 163
(2026-07-10).** The sibling repo's `n-player/bb_direct.py` (`build_paley_3mod8(p, c)`)
realizes `P(p)` for `p ≡ 3 (mod 8)` in **`(p+3)/2`** faces — block 0 is
`[p]*(m+1)+[-1]*m+[0,0]`, length `k+2` with `k=(p−1)/2`, `m=k//2`; note `(p+1)/2` is *even*
here (would allow ties) so `(p+3)/2` (odd) is the real count. Each face is one voter (columns
occupy disjoint value-bands), so removing 2 voters flips only margin-±1 edges, and only where
*both* removed voters back that edge's winner. For **11 of the 13** primes `p ≡ 3 (mod 8)` in
`[67, 331]` the construction contains a **degenerate voter** (column `k`) that backs the winner
on very few margin-1 edges, giving `(p+1)/4` "0-flip" partners; deleting `{k, a 0-flip partner}`
flips **0** edges → the tournament is bit-identical to `P(p)` (0 ties) at **`(p−1)/2`** faces.
Files verified (identical dominance, 0 ties): `paley{83_41,107_53,131_65,139_69,179_89,211_105,
227_113,251_125,283_141,307_153,331_165}face.txt`. The reduced set is **tight**: for p=331 no
further 2-voter deletion works (all `C(165,2)` break the 6-player property; min flips jumps 0→1025).
**Exceptions: `p = 67` and `p = 163`** — no 0-flip pair for *any* verifying `c` (min flips
`= (p−1)/2`), and a full deletion sweep confirms *every* 2-face deletion breaks validity
(`γ(P(67))=γ(P(163))=5`, all deletions drop `γ` to 4). These are exactly the two **Heegner
primes** (class number 1: `1,2,3,7,11,19,43,67,163`) that are `≡ 3 (mod 8)`; since the Heegner
list ends at 163, *every* `p ≡ 3 (mod 8)` with `p > 163` is predicted to reduce (untested past
331). All `(p−1)/2` counts here are still ≈ double the conjectured `(p+1)/4`. 6-player validity
for p=331 was checked via the domination-number characterization with an O(n²)-verified
`p`-cycle automorphism certificate (`paley331_165face.aut.txt`); verifier
`verify_6player_domination.py`. See `RESEARCH_LOG.md` (2026-07-10).

## The three categories

**① Deterministic → (p−1)/2 faces** — exactly the primes **p ≡ 7 (mod 8)**:
`7, 23, 31, 47, 71, 79, 103, 127, 151, …` (chain / Construction 7).

**② Deterministic → (p−1)/2 faces for `p ≡ 3 (mod 8)`** — **newbednay − 2 voters** ★
(2026-07-10), for every `p ≡ 3 (mod 8)` **except the Heegner primes 67 & 163**:
`83, 107, 131, 139, 179, 211, 227, 251, 283, 307, 331, …`. Supersedes Construction 6
here. The two Heegner exceptions get `(p+3)/2` (newbednay, not reducible).

**②′ Deterministic → p faces** — **every** Paley prime `p ≡ 3 (mod 4)` (Construction 6);
now only the universal fallback (e.g. still the deterministic option for 11, 19, 43, 59).

**③ Annealing reached (p−1)/2 for the small `p ≡ 3 mod 8`** (11, 19):
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
- **p ≡ 3 (mod 8), larger (43, 59, 67, 83, …):** annealing stalls, but there are now two
  deterministic options: **newbednay − 2 voters → `(p−1)/2`** ★ (for all `p ≡ 3 mod 8`
  except the Heegner primes 67 & 163), and for small `p` a **SAT solver** does even better —
  `P(43)` → **11 faces** (¶), `P(67)` → **17 faces** (‡), far under both Construction 6 and
  `(p−1)/2`. So: use SAT where it's feasible (small `p`); otherwise newbednay − 2 gives
  `(p−1)/2` for free (except 67, 163). Extending SAT to 59, 83, … is the natural next step.
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
