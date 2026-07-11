Intransitive Dice Generator
==

_Last updated: 2026-07-01_

Fewer Faces: a 9-Face 4-Player Set (`gen_9face_4player.py`)
===

The main construction below uses **171 faces** per die for four players. `gen_9face_4player.py` realizes the *same* four-player structure — the Paley tournament P(19) — with only **9 faces per die**.

The idea is to express P(19) as the **majority of `F = 9` linear orders** ("voters"). Each order `orders[t]` is a permutation of `{0,…,18}`; die `i` then takes one face per order,

```
die_i = { 19 * t + orders[t][i] : t = 0 … 8 }
```

The `19 * t` offset puts each order's faces in a disjoint band, so cross-order comparisons cancel and

```
bias(i, j) = sum over t of sign( orders[t][i] − orders[t][j] )
```

i.e. die `i` beats die `j` exactly when a majority of the 9 orders rank `i` above `j`. The script uses a seeded simulated-annealing search to find 9 orders whose majority relation equals P(19) (reproducible), builds the dice, and verifies them with the same `all_dice_win` check as `4_players_19_dice_static_analysis.py`.

Run it:

```
python gen_9face_4player.py
```

Result — **19 dice × 9 faces**, verified four-player:

```
matches Paley tournament P(19): True
all_dice_win (every 3-coalition is beaten by some die): True
winners-per-coalition distribution: {1: 399, 2: 513, 3: 57}
bias values: [-3, -1, 1, 3]  ->  max win probability ~ 0.5185
```

Every one of the C(19,3) = 969 triples of dice is beaten by some fourth die, so this is a valid four-player set. The trade-off for using far fewer faces is a smaller winning margin: the 171-face set wins about **59.3%** of the time, while this 9-face set is closer to **51.9%** (so the intransitive advantage, though real, needs more rolls to show up).

Intransitive Dice
===

[Intransitive dice](https://en.wikipedia.org/wiki/Intransitive_dice) refer to a set of dice that lack transitivity, for example:

Dice A: 2, 2, 4, 4, 9, 9.

Dice B: 1, 1, 6, 6, 8, 8.

Dice C: 3, 3, 5, 5, 7, 7.

If P(A > B) is the probability that the value rolled on Dice A is greater than that on Dice B, it can be verified that:

P(A > B) = P(B > C) = P(C > A) = 5/9 > 1/2

Thus, this set of dice is non-transitive.

n-Player Intransitive Dice
===
Intransitive dice can be extended to multiplayer scenarios, where there are n dice, and if n-1 dice are chosen, there will always be one remaining die that has a higher winning probability than the selected n-1 dice.

This situation is referred to as an [n-paradoxical tournament](https://oeis.org/A362137). In the linked sequence, n corresponds to n+1 players:

```1, 3, 7, 19, 67, 331, 1163```

Thus, 3 players require at least 7 dice, and 4 players require at least 19 dice.

In 1986, Oskar van Deventer constructed a set of [7 intransitive dice for 3 players](https://www.mathpuzzle.com/MAA/39-Tournament%20Dice/mathgames_07_11_05.html).

How to Use This Program
===
This program can generate n-player intransitive dice sets with prime numbers of dice. It accepts a prime number as input, determines the number of players based on the OEIS sequence above, and outputs the result. For example, with 7 dice:

```
python gen_intransitive_dice.py 7
Players amount: 3
found a dice set of size 7 of 3 faces each with 3 players
below is the dice set. Each column is a die, each row is one value of the die.
--  --  --  --  --  --  --
 3   2   1   0   6   5   4
10   8  13  11   9   7  12
17  20  16  19  15  18  14
--  --  --  --  --  --  --
```

Each column represents the values of one die. The number of rows corresponds to the number of faces on each die. Due to some mathematical properties, when the number of dice satisfies n % 8 = 7, the number of faces is smaller; otherwise, the faces may be very large.

4-Player
===
Inspired by [this source](https://github.com/NGeorgescu/math_problems/blob/main/intransitive.ipynb), I found that when n % 8 ≠ 7, the dice values can be balanced by repeating faces.

The link above provides a set of 23-face dice for 4 players. This program can generate a set of 19 dice with 171 faces each for 4 players:

```
python gen_intransitive_dice.py 19
Players amount: 4
found a dice set of size 19 of 171 faces each with 4 players
below is the dice set. Each column is a die, each row is one value of the die.
----  ----  ----  ----  ----  ----  ----  ----  ----  ----  ----  ----  ----  ----  ----  ----  ----  ----  ----
   0    18    17    16    15    14    13    12    11    10     9     8     7     6     5     4     3     2     1
  19    34    30    26    22    37    33    29    25    21    36    32    28    24    20    35    31    27    23
  38    52    47    42    56    51    46    41    55    50    45    40    54    49    44    39    53    48    43
  57    70    64    58    71    65    59    72    66    60    73    67    61    74    68    62    75    69    63
  76    88    81    93    86    79    91    84    77    89    82    94    87    80    92    85    78    90    83
  95   105    96   106    97   107    98   108    99   109   100   110   101   111   102   112   103   113   104
 114   122   130   119   127   116   124   132   121   129   118   126   115   123   131   120   128   117   125
 .....
```

On this Wikipedia [talk page](https://en.wikipedia.org/wiki/Talk:Intransitive_dice), someone seems to have arrived at the same result in 2021. While this isn’t new, it validates the program's correctness.

Although not fully tested, this program should produce correct results for all prime numbers. For example, it can generate a set of 5-player non-transitive dice as follows:

```
python gen_intransitive_dice.py 67
```

However, the time required for full verification would be extremely long.

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

Verifying a Dice Set (`verify_dice_set.py`)
===

Checks whether a dice file is a valid `n`-player intransitive set, using the same `bias` / `wins` / `all_dice_win` logic as `gen_intransitive_dice.py`. The file has one die per line (face values separated by spaces).

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
