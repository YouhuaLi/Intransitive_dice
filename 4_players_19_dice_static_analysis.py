import numpy as np
from collections import Counter
import itertools as it
import sympy as sp
from fractions import Fraction
from pprint import pprint
from tabulate import tabulate
import matplotlib.pyplot as plt
import colorsys

def plot_graph(w, title=None, figsize=5, start_node_radius = .1 , end_node_radius = 0.04 ):
    n,sorted_nodes  = len(w), sorted(w.keys())
    colors = [colorsys.hsv_to_rgb(i*5%n * 5/6/n, 1, 0.5) for i in range(n)]
    edges = [[i, k] for i, j in w.items() for k in j]
    angles = np.linspace(0, 2 * np.pi, len(sorted_nodes), endpoint=False)
    pos = {node: (np.sin(angle), np.cos(angle)) for node, angle in zip(sorted_nodes, angles)}
    edge_colors = [colors[u % n] for u, v in edges]
    node_colors = [colors[node % n] for node in sorted_nodes]
    fig, ax = plt.subplots(figsize=(figsize, figsize))
    [ax.scatter(*pos[node], color=node_colors[node], s=300, zorder=3) for node in sorted_nodes]
    [ax.text(pos[node][0], pos[node][1], str(node), color='white', fontsize=12,
             ha='center', va='center') for node in sorted_nodes]
    for (u, v), c in zip(edges,edge_colors):
        start, end  = np.array(pos[u]), np.array(pos[v])
        direction = end - start
        unit_direction = direction / np.linalg.norm(direction)
        start_short = start + direction * start_node_radius
        end_short = end - unit_direction * end_node_radius
        ax.annotate("",
                    xy=end_short, xycoords='data',
                    xytext=start_short, textcoords='data',
                    arrowprops=dict(arrowstyle="->", color=c))
    plt.axis('off'); plt.axis('equal')
    if title: plt.title(title)
    plt.show()

with open('4_players_19_dice.txt', 'r') as file:
    d = [list(map(int, line.split())) for line in file]
#print(d)

n = 19 #number of dice
p = 3 #number of dice to choose to be beaten
# define a function that shows by how much
has_winning_die = lambda s: Counter([j[0] for i in s for j in d if i!=j if wins(i,j)>0]).most_common(1)[0][1]==p

#Let's also define a win dictionary:
d_wins = lambda d: {i[0]:sorted(j[0] for j in d if wins(i,j)>0) for i in sorted(d)}

# a function which tells us by how much one wins over another
bias = lambda d1, d2: sum([(j<i)-(i<j) for i in d1 for j in d2])

# the sign of the win function, negative means the second die wins, positive means the first
wins = lambda d1,d2: np.sign(bias(d1,d2))
select_dice_that_beat = lambda i: [j[0] for j in d if i!=j if wins(i,j)>0]
die_that_beats_all = lambda q: [j for j in range(n) if all(j in k for k in q)]
has_unbeaten_dice = lambda d: [q for q in it.combinations([select_dice_that_beat(i) for i in d],p) if not die_that_beats_all(q)]

assert not has_unbeaten_dice(d)
#let's define a winning dictionary
w = d_wins(d)
#print(w)

# define a function that tells you which die will beat any three dice that are given to you.
def which_beats(dice):
    return {i for i,j in w.items() if all(die in j for die in dice)}

all_dice_win = lambda w: all(len(which_beats(i)) for i in it.combinations(list(w),p))
#make sure that all combinations of dice have a winning solution.
assert all_dice_win(w)

#w[0]=[]
#one last sanity double-check with a one-liner that checks if there always exists some number that is on all three lists for every combination of dice, this number represents the lowest face of the die
assert all(Counter([k[0] for j in i for k in d if sum([(i1<i2)-(i1>i2) for i1,i2 in zip(j,k)])>0]).most_common(1)[0][1]==p for i in it.combinations(d,3))
plot_graph(w, "Four-Player Intransitive Dice Win Graph")

#double check, what is the bias?
d1,d2 = d[:2]
win_fraction = (lambda x: Fraction(sum(x),len(x)))([i<j for i in d1 for j in d2])
print(f'{win_fraction} = {round(float(win_fraction)*100,2)}%')

#is this bias constant for all values?
bias_matrix = np.array([[bias(i,j) for i in d] for j in d])
print(tabulate(bias_matrix))

