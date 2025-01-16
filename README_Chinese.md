非传递骰子（intransitive dice）生成程序
==

非传递骰子
===

[非传递骰子](https://en.wikipedia.org/wiki/Intransitive_dice)是指一组不具有传递性的骰子，比如：


骰子A的点数： 2, 2, 4, 4, 9, 9.

骰子B的点数: 1, 1, 6, 6, 8, 8.

骰子C的点数: 3, 3, 5, 5, 7, 7.

如果P(A>B)是掷骰子A的点数大于骰子B的点数的概率，则可以验证：

P(A>B)=P(B>C)=P(C>A)=5/9>1/2

所以，这组骰子不具有传递性。

n-玩家的非传递骰子
===
非传递骰子可以扩展到多人，即有n个骰子，任选n-1个骰子，总能从剩下的骰子中找到一个骰子，使其获胜概率大于已被选的n-1个骰子。

这种情况被称为[n-paradoxical tournament](https://oeis.org/A362137)，这个连接中的n对应的是n+1个玩家的情况:

```1, 3, 7, 19, 67, 331, 1163```

所以，3个玩家至少需要7个骰子，4个玩家需要至少19个骰子。

1986年，Oskar van Deventer构造出了[3个玩家的7个非传递骰子](https://www.mathpuzzle.com/MAA/39-Tournament%20Dice/mathgames_07_11_05.html)。

本程序的使用
===
本程序可以打印构造质数数量的n-玩家非传递骰子。程序接受一个质数为参数，然后根据以上OEIS序列，决定玩家数量，打印结果，比如7个骰子：

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

以上每一列是一个骰子的点数。行数就是每个骰子的面数。因为一些数学上的原因，仅当骰子数量n % 8 = 7时，骰子的面数比较少，否则面数会非常多。

4-player
===
基本上是受了[这里](https://github.com/NGeorgescu/math_problems/blob/main/intransitive.ipynb)的启发。我发现，当n % 8≠7时，可以采取重复面数的方法，达到平衡点数的目的。

上述链接中，给出了一组23个面的4玩家骰子。本程序可以给出一组19个骰子的组合，每个骰子171个面：

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

在这个维基百科的[talk页面](https://en.wikipedia.org/wiki/Talk:Intransitive_dice)上，看到似乎有人在2021年就得到了同样的结果，所以这也不算新成果，但也侧面验证了程序的正确性。

虽然没有完全测试，但这个程序对所有的质数，应该都能产生正确的结果。比如，以下能生成一组5-玩家的非传递骰子：

```
python gen_intransitive_dice.py 67
```

但是完整验证所需时间会非常长。


