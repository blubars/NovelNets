import glob
import os
import csv
import errno
import re
import networkx as nx


def load_FB100_dataset(network_name, path="../data/facebook100/facebook100txt/*.txt"):
        entries = []
        pattern = "_attr.txt"
        files = glob.glob(path)
        network_files = [name for name in files if not re.search(pattern, os.path.basename(name)) and not re.search("facebook100", os.path.basename(name))]
        if network_name in [os.path.splitext(os.path.basename(name))[0] for name in network_files]:
            try:
                filepath = os.path.dirname(path) + '/' + network_name + '.txt'
                with open(filepath, "r") as f:
                    for line in csv.reader(f, delimiter='\t'):
                        entries.append(line)
            except IOError as exc:
                if exc.errno != errno.EISDIR:
                    raise  # Propagate other kinds of IOError.
            return entries
        else:
            raise ValueError("Network name '{}' not in file list.".format(network_name))


def get_size_sorted_network_names():
    files = glob.glob("../data/facebook100/facebook100txt/*.txt")
    pattern = "_attr.txt"
    network_files = [name for name in files if not re.search(pattern, os.path.basename(name)) and not re.search("facebook100", os.path.basename(name))]
    network_names = [os.path.splitext(os.path.basename(name))[0] for name in network_files]
    print(network_names)
    sizes = []

    for name in network_names:
        nodes = set()
        print("Building Graph for {}".format(name))
        data = load_FB100_dataset(name)
        for pair in data:
            nodes.add(pair[0])
            nodes.add(pair[1])
        sizes.append((name, len(nodes)))
    sizes.sort(key=lambda x: x[1], reverse=True)
    print(sizes)


def run_analysis(G):
    trans = nx.transitivity(G)
    giant_comp = max(nx.connected_component_subgraphs(G), key=len)
    diamter = nx.diameter(giant_comp)
    degree_assort = nx.degree_assortativity_coefficient(G)
    print((trans, diamter, degree_assort))
    return (trans, diamter, degree_assort)


if __name__ == "__main__":
    networks = [('USFCA72', 2682), ('Trinity100', 2613), ('Hamilton46', 2314), ('Bowdoin47', 2252), ('Amherst41', 2235), ('Swarthmore42', 1659), ('Simmons81', 1518), ('Haverford76', 1446), ('Reed98', 962), ('Caltech36', 769)]
    analyzed = []
    for name, size in networks:
        graph = nx.Graph()
        data = load_FB100_dataset(name)
        for pair in data:
            graph.add_nodes_from(pair)
        graph.add_edges_from(data)
        trans, diamter, degree_assort = run_analysis(graph)
        analyzed.append((name, trans, diamter, degree_assort))
    with open('"../data/facebook_metric.csv"', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for entry in analyzed:
            writer.writerow(entry)
