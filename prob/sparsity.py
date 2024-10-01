from pcalg import (
    compute_partial_correlation,
    compute_test_statistic,
    compute_pvalue,
)
import numpy as np
from networkx import DiGraph
from itertools import combinations


def minimal_imap(imap_samples, permutation, alpha):
    g = DiGraph()
    for i in permutation:
        g.add_node(i)
    for l, r in combinations(range(len(permutation)), 2):
        i, j = permutation[l], permutation[r]
        S = set(permutation[x] for x in range(r)) - {i}
        if compute_pvalue(imap_samples, i, j, list(S)) <= alpha:
            g.add_edge(i, j)

    return g


def get_imap_samples():
    return np.genfromtxt("data/imap_samples.csv", delimiter="")


def plot_graph(g):

    import matplotlib.pyplot as plt
    import networkx as nx

    pos = nx.spring_layout(g)
    nx.draw(g, pos, with_labels=True, node_size=700)

    plt.show()


if __name__ == "__main__":
    samples = get_imap_samples()
    print(samples.shape)
    p_a = [1, 2, 3, 4, 5]
    p_b = [5, 4, 1, 2, 3]
    p_c = [5, 4, 3, 2, 1]
    for permutation in [p_a, p_b, p_c]:
        print(minimal_imap(samples, permutation, 0.05))
