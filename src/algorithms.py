import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import copy
from networkx.algorithms.community.quality import modularity

########################
# Modularity Functions #
########################


def draw_partition_graph(G, partitions):
    plt.rc('axes.formatter', useoffset=False)
    pos = nx.spring_layout(G) # positions for all nodes
    for i, part in enumerate(partitions):
        nx.draw_networkx_nodes(G, pos,
                               nodelist=list(part),
                               node_color= np.random.rand(3,),
                               node_size=500,
                               alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
    plt.show()


def draw_modularity_plot(modularities):
    color = np.random.rand(3,)
    passes = [i+1 for i, value in enumerate(modularities)]
    plt.scatter(passes, modularities, c=color, s=50)
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.title("Modularity vs. Number of Passes")
    plt.ylabel("Modularity", size="x-large")
    plt.xlabel("Number of Passes", size="x-large")
    plt.show()


def normalized_mutual_information(test_partitions, actual_partitions):
    n = sum([len(x) for x in test_partitions])
    information = 0
    for t in test_partitions:
        for a in actual_partitions:
            n_xy = len(t & a) / n
            n_x = len(t) / n
            n_y = len(a) / n
            if n_xy > 0.0 and n_x > 0.0 and n_y > 0.0:
                information += n_xy*np.log2(n_xy/(n_x*n_y))
    h_test = sum([-len(t)/n*np.log2(len(t)/n) for t in test_partitions])
    h_actual = sum([-len(a)/n*np.log2(len(a)/n) for a in actual_partitions])
    return (2*information)/(h_actual+h_test)


def agglomerative_modularity(G):
    modularities = []
    # initial grouping where each node is in its own group
    best_partitions = [frozenset([n]) for n in G.nodes()]
    prev_modularity = -1000
    # modularity takes in the groupings as a set of nodes of G representing a partitioning
    curr_modularity = modularity(G, best_partitions)
    while curr_modularity > prev_modularity:
        merges = []
        prev_modularity = curr_modularity
        test_partitions = list(best_partitions)
        for i, g1 in enumerate(best_partitions):
            for j, g2 in enumerate(best_partitions):
                # Skip i=j and empty communities
                if j <= i or len(g1) == 0 or len(g2) == 0:
                    continue
                test_partitions[j] = g1 | g2
                test_partitions[i] = frozenset([])
                test_modularity = modularity(G, test_partitions)
                if test_modularity > curr_modularity:
                    curr_modularity = test_modularity
                    # add to the merging to list of merges as a tuple with delta Q as first element
                    # and the potential merge as the second element
                    merges.append((curr_modularity - prev_modularity, copy.deepcopy(test_partitions)))
                test_partitions[i] = g1
                test_partitions[j] = g2
        # in this implementation, tie breaking is first come first serve
        if len(merges) > 0:
            best_partitions = sorted(merges, key=lambda x: x[0], reverse=True)[0][1]
        else:
            best_partitions = test_partitions
        modularities.append(modularity(G, best_partitions))
    partitions = [frozenset(g) for g in sorted([g for g in best_partitions if len(g) > 0], key=lambda x: len(x), reverse=True)]
    return partitions, modularities

########################
# Centrality Functions #
########################


def weighted_degree_centrality(G, weight=None):
    if len(G) <= 1:
        return {n: 1 for n in G}

    if weight:
        s = 1 / sum([e[2] for e in G.edges(data="weight", default=0)])
        centrality = {n: w * s for n, w in G.degree(weight="weight")}
    else:
        s = 1 / (len(G) - 1)
        centrality = {n: k * s for n, k in G.degree()}
    return centrality

