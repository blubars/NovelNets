#! /usr/bin/env python3

#########################################################
# File Description:
#   Run analysis on book
# Authors: Hunter Wapman, Brian Lubars, Carl Mueller
# Date: 12/1/18
#########################################################

# TODO:
# section 25.15 in chronology doesn't exist, currently skipping.

#########################################################
# Imports
#########################################################
import json
import os
import csv
import argparse
import numpy as np
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
import matplotlib
import matplotlib.pyplot as plt
from collections import defaultdict

import algorithms as algos
from graphify import Graphify
from utils import get_sections_path
import plots

#########################################################
# Globals
#########################################################
ANALYSIS_PATH = '../data/analysis/'
TOTAL_NUM_SECTIONS = 192

#########################################################
# Function definitions
#########################################################
def get_chronological_order():
    # read json files of chronological order
    with open("../data/chronology.json", 'r') as f:
        chronology_json = json.loads(f.read())

    chapters = []
    for entry in chronology_json:
        entry = str(entry)

        if entry.replace('.', '', 1).isdigit():
            chapters.append(entry)
        else:
            continue

    with open("../data/sections_to_pages.json", 'r') as f:
        section_json = json.loads(f.read())

    chapters_to_sections = {}
    for entry in section_json:
        chapters_to_sections[entry['ch']] = entry['section']
        # print("{} --> {}".format(entry['ch'], entry['section']))

    sections = [chapters_to_sections[chapter] for chapter in chapters]

    num_sections = len(sections)
    num_unique_sects = len(set(sections))
    if num_sections != num_unique_sects:
        print("WARNING: something wrong in chronological order mapping.")
        print("Num sections:{}".format(num_sections))
        print("Num set(sections):{}".format(num_unique_sects))
    return sections


def analyze_centralities(G, weighted=True):
    # centrality measures
    centralities = [
        (nx.degree_centrality, "Degree", False),
        (algos.weighted_degree_centrality, "Weighted Degree", True),
        (nx.betweenness_centrality, "Betweenness", weighted),
        (nx.eigenvector_centrality, "Eigenvector", weighted),
        (nx.harmonic_centrality, "Harmonic (unweighted)", False)
    ]
    for cent_f, name, weight_param in centralities:
        print("Top 10 {} Centrality:".format(name))
        if weight_param:
            result = cent_f(G, weight="weight")
        else:
            result = cent_f(G)
        res_list = sorted(list(result.items()), key=lambda x:x[1], reverse=True)
        for i in range(10):
            node_id, cent = res_list[i]
            node_name = G.nodes[node_id]['name']
            print(" [{}] {}({}): {}".format(i, node_name, node_id, cent))
        print()


def analyze_assortativity(G):
    # Degree Assortativity
    result = nx.degree_assortativity_coefficient(G, weight="weight")
    print("Degree Assortativity Assorativity: {}".format(result))
    print()

    # Gender Associativity
    result = nx.attribute_assortativity_coefficient(G, "gender")
    print("Gender Assortativity Assorativity: {}".format(result))
    print()

    # Association Associativity
    result = nx.attribute_assortativity_coefficient(G, "association")
    print("Association Assortativity Assorativity: {}".format(result))
    print()


def generate_greedy_modularity_communities(G):
    print("Agglomerative Modularity:")
    # partitions, modularities = algos.agglomerative_modularity(G)
    # algos.draw_partition_graph(G, partitions)
    # algos.draw_modularity_plot(modularities)

    print("Greedy Modularity:")
    communities = greedy_modularity_communities(G, weight="weight")
    # print(communities)
    print("Num communities:{}".format(len(communities)))

    return communities

def analyze_neighborhood(gg, chronological=False):
    print("Neighborhood stability:")
    seq = get_section_sequence(chronological)
    stabilities = algos.neighborhood_stabilities(gg, seq)

    with open(os.path.join(ANALYSIS_PATH, 'neighborhood_stabilities-chronological_{}.json'.format(chronological)), 'w') as f:
        json.dump(stabilities, f)

def get_section_sequence(chronological=False):
    return get_chronological_order() if chronological else range(1, TOTAL_NUM_SECTIONS+1)

def analyze_attachment(gg, weighted=True):
    # does degree distribution follow a power law?
    # compare degree distribution to price's model
    # calculate 'age' of node in terms of section it first appears in
    # calculate ccdf of degree distribution
    if weighted:
        ks = sorted((k for (node,k) in gg.G.degree(weight='weight')), reverse=True)
    else:
        ks = sorted((k for (node,k) in gg.G.degree()), reverse=True)
    outfile = ANALYSIS_PATH + "degree_distr_ccdf.pdf"
    plots.plot_ccdf(ks, outfile)

def open_csv_file(name):
    out_csv_name = os.path.join(ANALYSIS_PATH, name)
    if not os.path.isdir(ANALYSIS_PATH):
        os.makedirs(ANALYSIS_PATH)
    try:
        csvf = open(out_csv_name, 'w', newline='')
        return csvf
    except:
        print("Failed to create csv file")
        return None

def analyze_dynamics(gg, chronological=False, weighted=False):
    seq = get_section_sequence(chronological)
    out_csv_name = 'dynamics-chronological_{}-weighted_{}.csv'.format(chronological, weighted)

    # geodesic_vs_degree
    seq = get_section_sequence(chronological)
    csvf = open_csv_file(out_csv_name)
    if not csvf:
        return
    writer = csv.writer(csvf)
    writer.writerow(["Section", "n", "avg degree", "avg geodesic len", "num components", "largest component size"])

    # for each section, calculate avg degree & mean geodesic
    for i, G in enumerate(gg.graph_by_sections(seq, aggregate=True)):
        num_components = 1
        largest_component = (-1,0)
        try:
            if weighted:
                avg_len = nx.average_shortest_path_length(G, weight="weight")
            else:
                avg_len = nx.average_shortest_path_length(G)
        except nx.NetworkXError:
            avg_len = 0
            num_components = 0
            for ci,C in enumerate(nx.connected_components(G)):
                ni = len(C)
                if ni > largest_component[1]:
                    subG = G.subgraph(C)
                    if weighted:
                        avg_len = nx.average_shortest_path_length(subG, weight="weight")
                    else:
                        avg_len = nx.average_shortest_path_length(subG)
                    largest_component = (ci, ni)
                num_components += 1

        if weighted:
            degs = [k for (node,k) in G.degree(weight='weight')]
        else:
            degs = [k for (node,k) in G.degree()]
        avg_degree = sum(degs) / len(degs)
        n = nx.number_of_nodes(G)
        largest_component_size = n if num_components == 1 else largest_component[1]
        print("Section:{}\tn:{}\n  avg deg:{}, avg geodesic:{}, num_components={}"
            .format(seq[i], n, avg_degree, avg_len, num_components))
        writer.writerow([seq[i], n, avg_degree, avg_len, num_components, largest_component_size])
    csvf.close()
    
def analyze_edge_distance_thresh():
    # Edge distance thresh impacts every part of the graph.
    # Higher the threshold, more dense and connected graph is.
    # Lower, less dense. Want to be lower so we can see 'real' connections
    # So, want to pick minimum viable threshold. Can decide by graphing.
    # Look for a phase transition.
    csvf = open_csv_file('edge_dist_analysis.csv')
    if not csvf:
        return
    writer = csv.writer(csvf)
    writer.writerow(["thresh", "n", "avg clustering", "num components", "GC size", "mean degree", "mean weighted degree"])

    threshs = [1, 2, 3, 5, 10, 15, 20, 50, 100, 200, 500]
    for thresh in threshs:
        g = Graphify(edge_thresh=thresh, edge_repeat_thresh=0, force_reload=True, autosave=False)
        largest_component = max(nx.connected_components(g.G), key=len)
        n = nx.number_of_nodes(g.G)
        avg_clus = nx.average_clustering(g.G)
        num_comp = nx.number_connected_components(g.G)
        gc_size = len(largest_component)
        mean_deg = sum(v for k,v in g.G.degree()) / n
        weighted_mean_deg = sum(v for k,v in g.G.degree(weight='weight')) / n
        writer.writerow([thresh, n, avg_clus, num_comp, gc_size, mean_deg, weighted_mean_deg])
    csvf.close()

def analyze_gender(gg, weighted=True):
    sequence = get_section_sequence()
    for G in gg.graph_by_sections(sequence, aggregate=True):
        last_G = G

    degrees_by_gender = defaultdict(defaultdict(list).copy)

    degrees = {
        'unweighted' : {node: degree for node, degree in G.degree()},
        'weighted' : {node: degree for node, degree in G.degree(weight='weight')}
    }

    for node in last_G.nodes():
        for degree_type, degree_type_vals in degrees.items():
            degree = degree_type_vals[node]

            degrees_by_gender[degree_type]['overall'].append(degree)
        
            gender = G.nodes[node].get('gender')

            if gender:
                degrees_by_gender[degree_type][gender].append(degree)


    calculated = defaultdict(dict)
    for degree_type, degree_type_vals in degrees_by_gender.items():
        for key, vals in degree_type_vals.items():
            avg = sum(vals) / len(vals)

            calculated[degree_type][key] = avg

    with open(os.path.join(ANALYSIS_PATH, 'gender.json'), 'w') as f:
        json.dump(calculated, f)

def analyze_communities(gg):
    sequence = get_section_sequence()
    for G in gg.graph_by_sections(sequence, aggregate=True):
        last_G = G

    auto_communities = generate_greedy_modularity_communities(G)

    labeled_communities = defaultdict(list)
    for node in G.nodes():
        community = G.nodes[node].get('association')
        name = G.nodes[node]['name']

        if not community:
            community = name

        labeled_communities[community].append(name)

    labeled_communities = [frozenset(l) for l in labeled_communities.values()]
    result = algos.normalized_mutual_information(auto_communities, labeled_communities)
    print(result)

    num_nodes = len(list(last_G.nodes()))
    matrix = [[0 for _ in range(num_nodes)] for _ in range(num_nodes)]
    unused_id = 0
    node_ids = {}
    for node in last_G.nodes():
        if node_ids.get(node, -1) == -1:
            node_ids[node] = unused_id
            unused_id += 1

        for _node in last_G.neighbors(node):
            if node_ids.get(_node, -1) == -1:
                node_ids[_node] = unused_id
                unused_id += 1

            matrix[node_ids[node]][node_ids[_node]] = 1

    indexed_labeled_communities = []
    for l in labeled_communities:
        indexed_labeled_communities.append([node_ids[x] for x in l])

    q = algos.calculate_modularity(matrix, indexed_labeled_communities)
    print(q)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Infinite Jest")
    parser.add_argument('--chronological', '-c', default=False, action="store_true", help="Analyze book in chronological order")
    parser.add_argument('--unweighted', '-u', default=False, action="store_true", help="Analyze book as a simple undirected graph")

    args = parser.parse_args()

    weighted = not args.unweighted

    print("Creating graphs!")
    gg = Graphify()

    print("Analyzing book!")
    analyze_communities(gg)
    # analyze_dynamics(gg, chronological=args.chronological, weighted=weighted)
    # analyze_gender(gg, weighted=weighted)
    # analyze_centralities(gg.G, weighted=weighted)
    # analyze_assortativity(gg.G)

    # analyze_neighborhood(gg, chronological=False)
    # analyze_neighborhood(gg, chronological=True)
    # display_chronologicality()
    # analyze_attachment(gg, weighted=weighted)
