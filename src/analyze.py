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
from graphify import Graphify
import json
import networkx as nx

#########################################################
# Globals
#########################################################
SECTION_PATH = '../data/current/sections/'
SAVE_GRAPH_PATH = '../data/graph/'
TOTAL_NUM_SECTIONS = 192

#########################################################
# Function definitions
#########################################################

def get_chronological_order():
    # read json files to extract chronological sect order
    chs = []
    with open("../data/chronology.json", 'r') as chrono_file:
        chrono_json = json.loads(chrono_file.read())
        for entry in chrono_json:
            if 'chapter' in entry:
                ch = str(entry['chapter'])
                if len(ch.split('.')) == 1:
                    ch += '.1'
                if ch == '25.15':
                    # TODO: fix this.
                    continue
                chs.append(ch)
    chs_to_sects = {}
    with open("../data/sections_to_pages.json", 'r') as sect_file:
        sect_json = json.loads(sect_file.read())
        for entry in sect_json:
            chs_to_sects[str(entry['ch'])] = entry['section']
            print("{} --> {}".format(entry['ch'], entry['section']))
    sections = [chs_to_sects[ch] for ch in chs]
    num_sections = len(sections)
    num_unique_sects = len(set(sections))
    if num_sections != num_unique_sects:
        print("WARNING: something wrong in chronological order mapping.")
        print("Num sections:{}".format(len(order)))
        print("Num set(sections):{}".format(len(set(order))))
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
    gg = Graphify(SECTION_PATH, 500, 50)
    sections = get_section_sequence(chronological)
    if load_from_file:
        gg.load(SAVE_GRAPH_PATH, sections)
    else:
        gg.process_book(sections)
    return gg

def analyze_dynamics(gg, seq):
    # for each section, calculate avg degree & mean geodesic
    for i,G in enumerate(gg.graph_by_sections(seq, aggregate=True)):
        num_components = 1
        try:
            avg_len = nx.average_shortest_path_length(G, weight="weight")
        except nx.NetworkXError:
            avg_len = 0
            num_components = 0
            largest_component = (-1,0)
            for ci,C in enumerate(nx.connected_component_subgraphs(G)):
                ni = nx.number_of_nodes(C)
                if ni > largest_component[1]:
                    avg_len = nx.average_shortest_path_length(C, weight="weight")
                    largest_component = (ci, ni)
                num_components += 1

        degs = [k for (node,k) in G.degree()]
        avg_degree = sum(degs) / len(degs)
        n = len(degs)
        print("Section:{}\tn:{}\n  avg deg:{}, avg geodesic:{}, num_components={}".format(seq[i], n, avg_degree, avg_len, num_components))

if __name__ == "__main__":
    print("Creating graphs")
    # first run: need to build graph from book text
    #gg = graphify_whole_book(load_from_file=False)
    #gg.save(SAVE_GRAPH_PATH)

    # second run: can load from saved graph files
    gg = graphify_whole_book(load_from_file=True)

    print("Analyzing book!")
    analyze_dynamics(gg, get_section_sequence())
    #analyze_centralities(gg.G)
    gg.web.draw()


