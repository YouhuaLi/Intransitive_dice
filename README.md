Intransitive Dice — minimizing the face count
==

_Last updated: 2026-07-10_

A set of dice is **n-player intransitive** if, for every coalition of `n−1` dice, some other
die beats all of them (an `(n−1)`-paradoxical tournament). See
[OEIS A362137](https://oeis.org/A362137) — `1, 3, 7, 19, 67, 331, 1163` are the fewest dice
needed for `2, 3, 4, 5, 6, 7` players.

This repo focuses on the **minimum number of faces per die**. The dominance graph is realized
as the **majority of `F` linear orders** ("voters"), one face per order; realizing the
**Paley tournament `P(p)`** (`p ≡ 3 mod 4` prime, `i` beats `j` iff `i − j` is a quadratic
residue) makes the `p` dice `(k+1)`-player intransitive. `F` = faces per die is the quantity we
minimize.

- Full per-prime face-count table and constructions: **`FACE_COUNTS.md`**
- Research log / session handoff: **`RESEARCH_LOG.md`**
- The original 171-face-per-die four-player generator (`gen_intransitive_dice.py`) is kept for
  reference but is far from optimal; the constructions below do much better.

Reducing the Number of Faces
===

The 171 faces produced by `gen_intransitive_dice.py` for four players are far from optimal. The key idea behind a smaller construction is to realise the required tournament as the **majority of `F` linear orders** ("voters"):

- Pick `p` dice whose dominance graph is a `k`-paradoxical tournament (the Paley tournament `P(p)`: die `i` beats die `j` iff `(i - j) mod p` is a quadratic residue).
- Encode it with `F` orders. Each die gets one face per order, offset by `p*t` so faces from different orders occupy disjoint ranges. Cross-order comparisons then cancel and

  ```
  bias(i, j) = sum over t of sign( order_t[i] - order_t[j] )
  ```

  i.e. die `i` beats die `j` exactly when a majority of the `F` orders rank `i` above `j`. Each die ends up with `F` faces.

Three ways to obtain the orders:

| Method | Faces per die | Notes |
| --- | --- | --- |
| **circulant** (default) | `p` | Deterministic closed form (Bednay & Bozóki 2013, Construction 6); no search, any `p ≡ 3 mod 4`. |
| **chain** | `(p-1)/2` | Deterministic, instant; only valid when `p % 8 == 7`. |
| **reduce** | minimum found | Simulated-annealing search for the fewest faces; great for small `p`, expensive for large `p`. |

Results (every set below is verified `k`-paradoxical):

| Players | Construction | Dice | Faces/die | Note |
| --- | --- | --- | --- | --- |
| 3 | reduce, `p=7` | 7 | **3** | vs Oskar's 6-face dice |
| 4 | reduce, `p=19` | 19 | **9** | vs 171 from the original program |
| 4 | chain, `p=23` | 23 | 11 | the NGeorgescu set |
| 5 | circulant, `p=67` | 67 | 67 | fewest dice |
| 5 | chain, `p=71` | 71 | **35** | a few more dice, about half the faces |

For four players, `19 dice x 9 faces` beats the previously published `23 dice x 11 faces` on both counts. For five players, the smallest face count comes from trading four extra dice (67 -> 71) for `(71-1)/2 = 35` faces via the deterministic chain construction; this set is provided in `5_players_71_dice.txt`.

Trade-off: fewer faces means a smaller winning margin. The 171-face four-player set wins about 59.3% of the time, while the 9-face set is closer to 53%.

Relation to the literature
---

The Paley tournament `P(p)` is `k`-paradoxical for large enough `p` (Graham & Spencer, *A constructive solution to a tournament problem*, Canad. Math. Bull. 14, 1971). Bozóki (*Nontransitive dice sets realizing the Paley tournaments*, Miskolc Math. Notes 15, 2014) gives an explicit dice set `D_p` realizing `P(p)` with **`p(p-1)/2` faces per die** (171 for `p=19`) and equal face-sums across dice. The reduced constructions here (e.g. 9 faces for `p=19`) use **fewer** faces than that published `D_p`, at the cost of unequal sums and a smaller margin. Pushing the face count below `p(p-1)/2` is the topic of Bednay & Bozóki, *Constructions for nontransitive dice sets* (Proc. 8th Japanese-Hungarian Symposium, 2013). No minimality claim is made for the face counts in the table above.

Paley Face Counts: the `newbednay − 2 voters` Reduction
===

Recent work (tracked in `FACE_COUNTS.md`, with a full log in `RESEARCH_LOG.md`) studies the
**minimum number of faces** needed to realize the Paley tournament `P(p)` as the majority of `F`
voters, for primes `p ≡ 3 (mod 4)`.

A key result for **`p ≡ 3 (mod 8)`**: the deterministic "newbednay" construction (the sibling
repo's `n-player/bb_direct.py`) realizes `P(p)` in `(p+3)/2` faces — but that set carries **two
redundant voters**. Deleting a *degenerate* voter (column `k = (p−1)/2`) together with one of its
`(p+1)/4` "0-flip" partners flips **no** edges, so the realized tournament is unchanged and the
face count drops to **`(p−1)/2`**. That matches what the chain construction gives for
`p ≡ 7 (mod 8)`, and is far below Construction 6's `p` faces.

The reduction succeeds for every `p ≡ 3 (mod 8)` tested in `[67, 331]` **except the two Heegner
primes `67` and `163`** (the imaginary quadratic fields of class number 1): for those, no such
reduction exists and *every* 2-face deletion breaks the intransitive property. Since the Heegner
list ends at 163, all larger `p ≡ 3 (mod 8)` are expected to reduce.

Verified `(p−1)/2`-face sets live in `best_results/paley<p>_<(p−1)/2>face.txt` for
`p = 83, 107, 131, 139, 179, 211, 227, 251, 283, 307, 331` — e.g. `P(331)` in **165** faces
(down from 167). Validity is verified through the **domination-number** characterization (a set is
a valid `n`-player set iff its dominance tournament has domination number `≥ n`, i.e. no dominating
set of size `n−1`), since the literal `C(p, n−1)` coalition enumeration is infeasible at this size;
see `verify_6player_domination.py` (it uses an `O(n²)`-checked automorphism certificate to make the
proof both fast and rigorous).

Unified Generator (`gen_unified.py`)
===

`gen_unified.py` produces dice for any prime (or auto-picks one for a given number of players) and verifies the result.

```
# auto-pick the smallest prime == 7 (mod 8) -> fewest faces (chain construction)
python gen_unified.py --players 5 --out 5_players_71_dice.txt   # 71 dice x 35 faces
python gen_unified.py --players 4                               # 23 dice x 11 faces
python gen_unified.py --players 3                               # 7  dice x 3  faces

# explicit prime
python gen_unified.py 19                                        # circulant: 19 dice x 19 faces
python gen_unified.py 19 --reduce                               # search fewest: 19 dice x 9 faces
python gen_unified.py 7  --chain                                # chain (needs p % 8 == 7)
```

Useful flags: `--out FILE` writes the dice (one die per line, space-separated), `--show-dice` prints them, `--reduce --max-faces N --budget SECONDS` tunes the search, `--no-paradox-check` skips the explicit enumeration.

**Overriding the player count (`--players` with a prime).** The player count is estimated from where `p` sits in A362137, but that estimate is only an upper bound and is **not monotonic**: e.g. `P(103)` is a valid **4-player** set (γ = 4 ⇒ S₃ holds) even though `103 ≥ 67` would suggest 5 players (S₄ actually fails). Pass `--players N` together with a prime to verify against the true count instead of the estimate:

```
python gen_unified.py 103 --chain                       # FAILS: checked as 5-player (S4), which P(103) lacks
python gen_unified.py 103 --chain --players 4 --out 4_players_103_dice.txt
# -> p = 103 -> 4 players  [overriding A362137 estimate of 5]
#    chain (F=(p-1)/2=51); 103 dice x 51 faces; 4-player property verified
python verify_dice_set.py 4 4_players_103_dice.txt      # VALID 4-player set (checks all C(103,3) coalitions)
```

Verifying a Dice Set
===

**`verify_dice_set.py`** — checks whether a dice file is a valid `n`-player intransitive set by enumerating every coalition, using the same `bias` / `wins` / `all_dice_win` logic as `gen_intransitive_dice.py`. The file has one die per line (face values separated by spaces).

```
python verify_dice_set.py <player_count> <dice_set_file>
```

It prints `VALID` (exit code 0) with statistics, or `INVALID` (exit code 1) together with the coalitions of `player_count - 1` dice that no other die can beat. Example:

```
$ python verify_dice_set.py 5 5_players_71_dice.txt
VALID 5-player intransitive dice set.
  dice           : 71
  faces per die  : 35
  coalitions     : checked all C(71,4) = 971635; each is beaten by at least one other die
```

**`verify_6player_domination.py`** — for large sets where the `C(p, n−1)` enumeration is infeasible (e.g. `C(331,5) ≈ 3.3e9`), it verifies the equivalent **domination-number** condition (valid `n`-player ⇔ tournament domination number `≥ n`), optionally taking an `O(n²)`-checked automorphism certificate to make the proof fast and rigorous:

```
python verify_6player_domination.py best_results/paley331_165face.txt best_results/paley331_165face.aut.txt
```
