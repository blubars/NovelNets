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
import pandas as pd
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import argparse
import numpy as np
from networkx.algorithms.community import greedy_modularity_communities
import algorithms as algos
from graphify import Graphify
from utils import get_sections_path

#########################################################
# Globals
#########################################################
ANALYSIS_PATH = '../data/analysis/'
TOTAL_NUM_SECTIONS = 192

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
        (nx.degree_centrality, "Degree"),
        (algos.weighted_degree_centrality, "Weighted Degree"),
        (nx.betweenness_centrality, "Betweenness"),
        (nx.eigenvector_centrality, "Eigenvector"),
        (nx.harmonic_centrality, "Harmonic")
    ]
    for cent_f, name in centralities:
        print("Top 10 {} Centrality:".format(name))
        # TODO: fix this, take weight to degree centrality.
        if name is "Degree" or "Weighted Degree":
            result = cent_f(G)
        elif weighted:
            result = cent_f(G, weight="weight") # deg. cent. doesn't take weight
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


def analyze_modularity(G):
    print("Agglomerative Modularity:")
    # partitions, modularities = algos.agglomerative_modularity(G)
    # algos.draw_partition_graph(G, partitions)
    # algos.draw_modularity_plot(modularities)

    print("Greedy Modularity:")
    communities = greedy_modularity_communities(G, weight="weight")
    print(len(communities))
    algos.draw_partition_graph(G, communities)

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
    #for section in range(0, len(ks)+1, 2):
    #for G in gg.graph_by_sections(seq, aggregate=True):
    fig = plt.figure(1)
    bins = [k+1 for k in range(max(ks)+1)]
    cumbins = [0 for k in range(max(ks)+1)]
    for k in ks:
        cumbins[k] += 1
    print("Nodes with 0 citations: {}%".format(cumbins[k]/len(cumbins)))
    for i in range(len(cumbins)-2, -1, -1):
        cumbins[i] = (cumbins[i+1] + cumbins[i])
    for i in range(len(cumbins)):
        cumbins[i] /= len(cumbins)
    plt.loglog(bins, cumbins)
    plt.title("Degree Distribution CCDF")
    plt.ylabel("Compl. Cumulative Distr Function")
    plt.xlabel("Degree, $k$")
    plt.legend()
    plt.tight_layout()
    fname = "degree_distr_ccdf.pdf"
    plt.savefig(ANALYSIS_PATH + fname)

def analyze_dynamics(gg, chronological=False, weighted=True):
    seq = get_section_sequence(chronological)
    out_csv_name = ANALYSIS_PATH + 'dynamics-chronological_{}-weighted_{}.csv'.format(chronological, weighted)
    if not os.path.isdir(ANALYSIS_PATH):
        os.makedirs(ANALYSIS_PATH)
    try:
        csvf = open(out_csv_name, 'w', newline='')
        writer = csv.writer(csvf)
    except:
        print("Failed to create csv file, quitting")
        return
    writer.writerow(["Section", "n", "avg degree", "avg geodesic len", "num components", "largest component size"])

    # for each section, calculate avg degree & mean geodesic
    for i, G in enumerate(gg.graph_by_sections(seq, aggregate=True)):
        num_components = 1
        largest_component = (-1,0)
        try:
            avg_len = nx.average_shortest_path_length(G, weight="weight")
        except nx.NetworkXError:
            avg_len = 0
            num_components = 0
            for ci,C in enumerate(nx.connected_component_subgraphs(G)):
                ni = nx.number_of_nodes(C)
                if ni > largest_component[1]:
                    avg_len = nx.average_shortest_path_length(C, weight="weight")
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

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Infinite Jest")
    parser.add_argument('--chronological', '-c', default=False, action="store_true", help="Analyze book in chronological order")
    parser.add_argument('--unweighted', '-b', default=False, action="store_true", help="Analyze book as a simple undirected graph")

    args = parser.parse_args()

    weighted = not args.unweighted

    print("Creating graphs!")
    gg = Graphify()

    print("Analyzing book!")
    # analyze_dynamics(gg, chronological=args.chronological, weighted=weighted)
    # analyze_centralities(gg.G, weighted=weighted)
    # analyze_assortativity(gg.G)
    # analyze_modularity(gg.G)

    analyze_neighborhood(gg, chronological=False)
    analyze_neighborhood(gg, chronological=True)
    # display_chronologicality()
    # analyze_attachment(gg, weighted=weighted)
