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

from graphify import Graphify
from utils import get_sections_path

#########################################################
# Globals
#########################################################
SAVE_GRAPH_PATH = '../data/graph/'
ANALYSIS_PATH = '../data/analysis/'
TOTAL_NUM_SECTIONS = 192

#########################################################
# Function definitions
#########################################################
def plot_df(df, x_name, y_name, title, logx=False):
    fig = plt.figure(1)
    X = df[x_name]
    Y = df[y_name]
    plt.scatter(X, Y)
    plt.plot(X, Y)
    plt.title(title)
    plt.ylabel(y_name)
    plt.xlabel(x_name)
    if logx:
        plt.xscale('log')
    plt.tight_layout()
    fname = x_name.lower() + '_vs_' + y_name.lower() + ".pdf"
    fname = fname.replace(" ", "_")
    plt.savefig(ANALYSIS_PATH + fname)
    plt.close(fig)

def get_chronological_order():
    # read json files to extract chronological sect order
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
        (nx.betweenness_centrality, "Betweenness"),
        (nx.eigenvector_centrality, "Eigenvector")
    ]
    for cent_f, name in centralities:
        print("Top 10 {} Centrality:".format(name))
        # TODO: fix this, take weight to degree centrality.
        if name is "Degree":
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

def get_section_sequence(chronological=False):
    return get_chronological_order() if chronological else range(1,TOTAL_NUM_SECTIONS+1)

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

def open_csv_file(name):
    out_csv_name = ANALYSIS_PATH + name
    if not os.path.isdir(ANALYSIS_PATH):
        os.makedirs(ANALYSIS_PATH)
    try:
        csvf = open(out_csv_name, 'w', newline='')
        return csvf
    except:
        print("Failed to create csv file")
        return None

def analyze_dynamics(gg, chronological=False, weighted=True):
    # geodesic_vs_degree
    seq = get_section_sequence(chronological)
    csvf = open_csv_file('geodesic_vs_degree.csv')
    if not csvf:
        return
    writer = csv.writer(csvf)
    writer.writerow(["Section", "n", "avg degree", "avg geodesic len", "num components", "largest component size"])

    # for each section, calculate avg degree & mean geodesic
    for i,G in enumerate(gg.graph_by_sections(seq, aggregate=True)):
        num_components = 1
        largest_component = (-1,0)
        try:
            avg_len = nx.average_shortest_path_length(G, weight="weight")
        except nx.NetworkXError:
            avg_len = 0
            num_components = 0
            for ci,C in enumerate(nx.connected_components(G)):
                ni = len(C)
                if ni > largest_component[1]:
                    subG = G.subgraph(C)
                    avg_len = nx.average_shortest_path_length(subG, weight="weight")
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


def make_plots():
    #df = pd.read_csv(ANALYSIS_PATH + 'geodesic_vs_degree.csv')
    #plot_df(df, "avg degree", "avg geodesic len", "Attachment: Degree vs Avg Geodesic Path, By Section")
    #plot_df(df, "n", "avg geodesic len", "Attachment: Log(n) vs Avg Geodesic Path", logx=True)
    df = pd.read_csv(ANALYSIS_PATH + 'edge_dist_analysis.csv')
    plot_df(df, "thresh", "GC size", "Threshold choice: Giant Component Size")
    plot_df(df, "thresh", "avg clustering", "Threshold choice: Clustering Coefficient")
    plot_df(df, "thresh", "mean weighted degree", "Threshold choice: Weighted Mean Degree")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Infinite Jest")
    parser.add_argument('--chrono', '-c', help="Analyze book in chronological order", action="store_true")
    parser.add_argument('--unweighted', '-u', help="Analyze book without edge weights", action="store_true")
    parser.add_argument('--make_plots', '-p', help="Make plots", action="store_true")
    args = parser.parse_args()
    chronological = True if args.chrono else False
    weighted = False if args.unweighted else True

    print("Creating graphs")
    gg = Graphify()

    print("Analyzing book!")
    #analyze_edge_distance_thresh()
    #analyze_dynamics(gg, chronological=chronological, weighted=weighted)
    #analyze_centralities(gg.G, weighted=weighted)
    #analyze_attachment(gg, weighted=weighted)
    if args.make_plots:
        make_plots()


