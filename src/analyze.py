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

def analyze_centralities(G):
    # centrality measures
    centralities = [
        (nx.degree_centrality, "Degree"),
        (nx.betweenness_centrality, "Betweenness"),
        (nx.eigenvector_centrality, "Eigenvector")
    ]
    for cent_f, name in centralities:
        print("Top 10 {} Centrality:".format(name))
        result = cent_f(G)
        #result = cent_f(G, weight="weight") # deg. cent. doesn't take weight
        res_list = sorted(list(result.items()), key=lambda x:x[1], reverse=True)
        for i in range(10):
            node_id, cent = res_list[i]
            node_name = G.nodes[node_id]['name']
            print(" [{}] {}({}): {}".format(i, node_name, node_id, cent))
        print()

def get_section_sequence(chronological=False):
    return get_chronological_order() if chronological else range(1,TOTAL_NUM_SECTIONS+1)

def graphify_whole_book(chronological=False, load_from_file=False):
    # build a graph per section.
    gg = Graphify(get_sections_path(), 500, 50)
    sections = get_chronological_order() if chronological else range(1,TOTAL_NUM_SECTIONS+1)
    if load_from_file:
        gg.load(SAVE_GRAPH_PATH, sections)
    else:
        gg.process_book(sections)
    return gg

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

def analyze_dynamics(gg, seq, weighted=True):
    # geodesic_vs_degree
    out_csv_name = ANALYSIS_PATH + 'geodesic_vs_degree.csv'
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
    for i,G in enumerate(gg.graph_by_sections(seq, aggregate=True)):
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
    # plot results.
    df = pd.read_csv(out_csv_name)
    plot_df(df, "avg degree", "avg geodesic len")

def make_plots():
    df = pd.read_csv(ANALYSIS_PATH + 'geodesic_vs_degree.csv')
    plot_df(df, "avg degree", "avg geodesic len", "Attachment: Degree vs Avg Geodesic Path, By Section")
    plot_df(df, "n", "avg geodesic len", "Attachment: Log(n) vs Avg Geodesic Path", logx=True)

if __name__ == "__main__":
    print("Creating graphs")
    # first run: need to build graph from book text
    #gg = graphify_whole_book(load_from_file=False, chronological=False)
    #gg.save(SAVE_GRAPH_PATH)

    # second run: can load from saved graph files
    gg = graphify_whole_book(load_from_file=True)

    print("Analyzing book!")
    #analyze_dynamics(gg, get_section_sequence())
    #analyze_centralities(gg.G)
    analyze_attachment(gg, weighted=False)
    #make_plots()
    #gg.web.draw()


