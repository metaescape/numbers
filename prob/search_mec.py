import numpy as np
import networkx as nx
from collections import deque


def covered_edge_neighbors(dag):
    result = []
    for node in dag.nodes:
        for neighbor in dag.neighbors(node):
            if set(dag.predecessors(neighbor)) == set(
                dag.predecessors(node)
            ) | set([node]):

                # deepcopy dag
                new_dag = dag.copy()
                # reverse edge
                new_dag.remove_edge(node, neighbor)
                new_dag.add_edge(neighbor, node)
                result.append(new_dag)

    return result


def search_mec(starting_dag, ending_dag):
    target = frozenset(ending_dag.edges)

    q = deque([(starting_dag, [starting_dag])])
    visited = set([frozenset(starting_dag.edges)])
    while q:
        current, path = q.popleft()
        if frozenset(current.edges) == target:
            return path[:-1]
        for neighbor in covered_edge_neighbors(current):
            if frozenset(neighbor.edges) not in visited:
                q.append((neighbor, path + [current]))
                visited.add(frozenset(neighbor.edges))

    return []


def load_graphs(num_examples=3):
    examples = []
    for ix in range(num_examples):
        a1 = np.loadtxt(f"data/mec_examples/starting_dag{ix}.csv")
        a2 = np.loadtxt(f"data/mec_examples/ending_dag{ix}.csv")
        starting_dag = nx.from_numpy_array(a1, create_using=nx.DiGraph)
        ending_dag = nx.from_numpy_array(a2, create_using=nx.DiGraph)
        examples.append((starting_dag, ending_dag))
    return examples


if __name__ == "__main__":
    examples = load_graphs(3)

    print(examples[1][0])

    # PART A
    for starting_dag, _ in examples:
        num_neighbors = len(covered_edge_neighbors(starting_dag))
        print(f"Number of neighbors: {num_neighbors}")

    # PART B
    for starting_dag, ending_dag in examples:
        path = search_mec(starting_dag, ending_dag)
        print(f"Length of path: {len(path)}")
