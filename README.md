Intransitive Dice Generator
==

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
This program can generate n-player intransitive dice sets with prime numbers of dice. It accepts an exponent as input, determines the number of players based on the OEIS sequence above, and outputs the result. For example, with 7 dice:

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

For certain reasons, **not all prime numbers can produce valid intransitive dice**. For example, when the parameter equals 67, the resulting dice are not valid 5-layer dice, but when the parameter is 71, they are.

```
python gen_intransitive_dice.py 71
```

However, the runtime will be long.
