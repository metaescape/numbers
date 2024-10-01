import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.stats import norm
from networkx import Graph
from itertools import combinations
from collections import defaultdict


def compute_partial_correlation(samples, i, j, S):
    """
    Compute the partial correlation between variables i and j given the set S of conditioning variables.
    """

    # regression of i on S

    i, j = i - 1, j - 1
    if S == []:
        return np.corrcoef(samples[:, i], samples[:, j])[0, 1]
    S = [x - 1 for x in S]
    reg_i = LinearRegression().fit(samples[:, S], samples[:, i])
    residuals_i = samples[:, i] - reg_i.predict(samples[:, S])
    reg_j = LinearRegression().fit(samples[:, S], samples[:, j])
    residuals_j = samples[:, j] - reg_j.predict(samples[:, S])
    return np.corrcoef(residuals_i, residuals_j)[0, 1]


def compute_test_statistic(samples, i, j, S):
    pcor = compute_partial_correlation(samples, i, j, S)
    weight = np.sqrt(samples.shape[0] - len(S) - 2)
    return np.arctanh(pcor) * weight


def compute_pvalue(samples, i, j, S):
    test_statistic = compute_test_statistic(samples, i, j, S)
    return 2 * (1 - norm.cdf(np.abs(test_statistic)))


def pcalg_skeleton(samples, alpha):
    """
    Estimate the skeleton of a DAG using the PC algorithm.
    """

    # initialize the skeleton
    n = samples.shape[1]
    g = Graph()
    g.add_nodes_from(range(1, n + 1))
    # full connected graph
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            g.add_edge(i, j)

    # breakpoint()
    d = 0
    s = defaultdict(set)
    while True:
        empty = True
        for i, j in g.edges:
            S = []
            markov_blanket = set(
                list(g.neighbors(i)) + list(g.neighbors(j))
            ) - {i, j}
            for S in combinations(markov_blanket, d):
                if compute_pvalue(samples, i, j, list(S)) > alpha:
                    g.remove_edge(i, j)
                    empty = False
                    s[(i, j)].add(S)
                    break
        if empty:
            break
        d += 1
    return g, s


def pcalg_orient(skeleton, separator_function):

    unshielded_colliders = set()

    for i, j in combinations(skeleton.nodes, 2):
        for k in set(skeleton.nodes) - {i, j}:
            if (
                skeleton.has_edge(i, k)
                and skeleton.has_edge(k, j)
                and not skeleton.has_edge(i, j)
            ):
                # print(i, k, j)
                iset = separator_function[(i, j)]
                all_conditions = set()
                for x in iset:
                    all_conditions.update(x)

                if k not in all_conditions:
                    unshielded_colliders.add((i, k, j))
    return unshielded_colliders


if __name__ == "__main__":
    pcalg_samples = np.genfromtxt("data/pcalg_samples.csv", delimiter="")
    print(pcalg_samples.shape)
    print(
        f"compute_partial_correlation(pcalg_samples, 1, 7, []) ≈ {compute_partial_correlation(pcalg_samples, 1, 7, []):.4f}"
    )
    print(
        f"compute_partial_correlation(pcalg_samples, 1, 7, [3, 4]) ≈ {compute_partial_correlation(pcalg_samples, 1, 7, [3, 4]):.4f}"
    )
    print(
        f"compute_partial_correlation(pcalg_samples, 1, 4, []) ≈ {compute_partial_correlation(pcalg_samples, 1, 4, []):.4f}"
    )
    print(
        f"compute_partial_correlation(pcalg_samples, 1, 4, [2, 3]) ≈ {compute_partial_correlation(pcalg_samples, 1, 4, [2, 3]):.4f}"
    )
    print(
        f"compute_test_statistic(pcalg_samples, 1, 7, [3, 4]) ≈ {compute_test_statistic(pcalg_samples, 1, 7, [3, 4]):.4f}"
    )
    print(
        f"compute_test_statistic(pcalg_samples, 1, 7, []) ≈ {compute_test_statistic(pcalg_samples, 1, 7, []):.4f}"
    )
    print(
        f"compute_test_statistic(pcalg_samples, 1, 4, [2, 3]) ≈ {compute_test_statistic(pcalg_samples, 1, 4, [2, 3]):.4f}"
    )
    print(
        f"compute_pvalue(pcalg_samples, 1, 7, [3, 4]) ≈ {compute_pvalue(pcalg_samples, 1, 7, [3, 4]):.4f}"
    )
    print(
        f"compute_pvalue(pcalg_samples, 1, 7, []) ≈ {compute_pvalue(pcalg_samples, 1, 7, []):.4f}"
    )
    print(
        f"compute_pvalue(pcalg_samples, 1, 4, [2, 3]) ≈ {compute_pvalue(pcalg_samples, 1, 4, [2, 3]):.4f}"
    )
    g, s = pcalg_skeleton(pcalg_samples[:500], 0.05)
    print(g.edges)
    print(g)

    print(pcalg_skeleton(pcalg_samples[:500], 0.2)[0])
    print(pcalg_skeleton(pcalg_samples[:500], 0.001)[0])
    print(pcalg_orient(g, s))
