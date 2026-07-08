# SAT face-minimization for Paley intransitive dice

Finds the minimum number of faces `d` to realize the Paley tournament `P(p)`
(`p ≡ 3 mod 4` prime) as a dice set = majority of `d` linear orders. This is the
**strongest method for small/medium p** (rank/voter encoding; beats constructions and
annealing). For large p where SAT is infeasible, see `../bilevel/`.

## Encoding (rank / voter)

Variables `V(X,Y,i,i)` = "die X's band-`i` face > die Y's band-`i` face". Transitivity per
band makes each face-slot a total order of the dice; the winner of each tournament edge must
take `⌊d/2⌋+1` of the `d` diagonal comparisons. Reconstructed face values are automatically a
permutation of `1..p·d` (banded by slot). Uses PySAT (`Cadical300` by default).

**Column-permutation symmetry breaking** (the `d` face-slots are interchangeable → `d!`
symmetry) is decisive on hard instances — it lex-orders adjacent columns. It slightly slows
tiny SAT cases but is essential for the hard ones.

## Files

| file | what |
|---|---|
| `sat_solve.py` | Main solver. Column-lex SB + optional equal-sum. Finds a d-face realization or reports UNSAT. |
| `sat_paley_sb.py` | Full **Paley-automorphism** SB (all `x→a·x+b`, a a QR). Much stronger pruning — for **UNSAT / minimality** proofs. |
| `lex.py` | Lex-leader `A ≤_lex B` constraint (unit-tested: `python lex.py`). |

## Usage

```
python sat_solve.py <p> <d> [solver] [budget_s] [symbreak 0/1] [eqsum 0/1] [eqsum_enc]
python sat_paley_sb.py <p> <d> [solver]
```

Examples:
```
python sat_solve.py 67 17               # find a 17-face P(67) set (SAT, ~hours) -> paley67_17face.txt
python sat_solve.py 19 3                # UNSAT (proves P(19) needs > 3)
python sat_solve.py 67 17 cadical300 0 1 1   # equal-sum (sum-balanced) variant (kmtotalizer)
python sat_paley_sb.py 23 5            # attack P(23) d=5 UNSAT with full automorphism SB
```

Solvers to try: `cadical300`, `cadical195`, `kissat404` (strong at SAT), `glucose42`.
A verified SAT solution is written to `paley<p>_<d>face.txt` (verify with `../bilevel/verify.py`).

## Known results (this = the conjecture `d = least odd ≥ (p+1)/4`, 8/8)

`P(19)=5, P(23)=7, P(31)=9, P(43)=11, P(47)=13, P(59)=15, P(67)=17, P(71)=19`.
Optimality PROVEN only for `p=11,19` (`d−2` is UNSAT, instant). `P(23) d=5` is an open,
genuinely hard instance (SAT + full-automorphism-SB + Kissat all ran many hours, no result).

## Gotchas (see `../RESEARCH_LOG.md`)

- These scripts inline `qr_tournament` and import nothing from the sibling repo — because that
  repo's `diceset.py` needs Python 3.11 (`typing.Self`) while the `pysat`-enabled `python3` here
  is 3.10. Keep them self-contained.
- **pysat's CaDiCaL ignores `solve_limited`/`interrupt`** — the `budget_s` arg silently does
  nothing for CaDiCaL. Enforce time limits with an OS `kill` / RSS watchdog, or run unbounded
  in the background and stop manually.
- **Equal-sum blows up with `totalizer`** (91M clauses once OOM-froze the machine). Default is
  `kmtotalizer` (~14× smaller). Run ONE heavy solver at a time; watch memory/swap.
- To prove minimality, run `sat_paley_sb.py` at `d = (target)−2`; validate its soundness first
  by confirming a known-SAT instance stays SAT under the same SB.
