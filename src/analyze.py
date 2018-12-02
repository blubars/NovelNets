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
SECTION_PATH = '../data/txt/sections/'
#TOTAL_NUM_SECTIONS = 192
TOTAL_NUM_SECTIONS = 10

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

def graphify_whole_book(chronological=False):
    # build a graph per section.
    gg = Graphify(SECTION_PATH, 500, 50)
    sections = get_chronological_order() if chronological else range(1,TOTAL_NUM_SECTIONS+1)
    gg.process_book(sections)
    return gg

if __name__ == "__main__":
    print("Analyzing book!")
    gg = graphify_whole_book()
    analyze_centralities(gg.G)



