#! /usr/bin/env python3

#########################################################
# File Description:
#   Turn a book, delimited into sections, into a graph.
# Authors: Hunter Wapman, Brian Lubars, Carl Mueller
# Date: 11/16/18
#########################################################

# 1. read in named entities
# 2. for each section:
#    a. recognize entities
#    b. link entities
#    c. graph

# Problems & ideas to improve:
# 1. smooth weights over sections, don't count edges
#    too many times within one interaction
# 2. minimum threshold: don't include edges if only 
#    mentioned once? could just be talking about someone.
#     -- how do we know if someone's there vs. being
#        talked about?
# 3. it seems to be matching multiple times, 
#    if multiple patterns even within one entity apply
# 4. doesn't match across '.', e.g. 'Comp. Director'

#########################################################
# Imports
#########################################################
import os
from collections import defaultdict
from copy import deepcopy
import networkx as nx
import json
import math
from utils import get_entities, get_entities_hash
import text_io
import ner
import sys
from pprint import pprint
#########################################################
# Globals
#########################################################
SAVE_GRAPH_PATH = '../data/graph/'
DEBUG = 1

#########################################################
# Function definitions
#########################################################
# util to print list w/ indentation
def print_list(lst, indent=2):
    indstr = ""
    for i in range(indent):
        indstr += ' '
    for item in lst:
        print("{}{}".format(indstr, item))

def print_debug(level, s):
    if DEBUG >= level:
        print(s)

# store a snapshot of the graph in time.
# just a collection of vertices & edges right now.
class GraphSnapshot:
    def __init__(self, V=set(), E=defaultdict(lambda: defaultdict(float)), section=None, section_length=None):
        self.section = section
        self.section_length = section_length
        self.V = V
        # edgelist is dict of dicts of weights.
        #   E[key1][key2] = weight
        self.E = E

    def __str__(self):
        s_str = "** SECTION {} **\n".format(self.section)
        v_str = "  Nodes:\n"
        for v in self.V:
            v_str += "    {}\n".format(v)
        e_str = "  Edges:\n"
        for k1, innerdict in self.E.items():
            for k2, v in innerdict.items():
                e_str += "    ({}<->{}: {})\n".format(k1, k2, v)
        return s_str + v_str + e_str

    def merge(self, other):
        merged_V = self.V | other.V
        merged_E = deepcopy(self.E)
        for k1, innerdict in other.E.items():
            for k2, v in innerdict.items():
                merged_E[k1][k2] += v
        g = GraphSnapshot(merged_V, merged_E)
        return g

    def delta(self, other):
        delta_V = self.V - other.V
        # TODO: how to handle difference btw edges?
        # might want to treat edges as binary rather than weighted 
        # for this purpose.
        delta_E = deepcopy(self.E)
        for k1, innerdict in other.E.items():
            for k2, v in innerdict.items():
                delta_E[k1][k2] -= v
        return GraphSnapshot(delta_V, delta_E)

    def save(self, path):
        filepath = "{}/{}-snapshot.json".format(path, self.section)
        data = dict()
        data["section_id"] = self.section
        data["section_length"] = self.section_length
        data["edges"] = self.E
        data["nodes"] = list(self.V) if type(self.V) is set else self.V
        with open(filepath, 'w') as fp:
            json.dump(data, fp, sort_keys=True, indent=4)

    def load(self, path):
        filepath = "{}/{}-snapshot.json".format(path, self.section)
        with open(filepath, 'r') as fp:
            data = json.load(fp)
            self.section = data["section_id"]
            self.section_length = data["section_length"]
            self.E = data["edges"]
            self.V = set(data["nodes"])

    def getNXGraph(self):
        G = nx.Graph()
        entities = get_entities()

        for entity in self.V:
            add_node_attributes(G, entities, entity)
        for node1, innerdict in self.E.items():
            for node2, v in innerdict.items():
                G.add_edge(node1, node2, weight=v)
        return G


def add_node_attributes(G, entities, entity):
    entity_attributes = deepcopy(entities[entity]['attributes'])
    entity_attributes['name'] = entity

    if entity not in G.nodes():
        G.add_node(entity, **entity_attributes)
    else:
        for attribute, value in entity_attributes.items():
            G.nodes[entity][attribute] = value


class Graphify:
    def __init__(self, edge_thresh=50, edge_repeat_thresh=50, data_path=SAVE_GRAPH_PATH, sections=range(1, 193), force_reload=False, autosave=True):
        self.G = nx.Graph()
        self.people = set()
        self.edge_threshold = edge_thresh
        self.edge_repeat_threshold = edge_repeat_thresh
        self.entities = get_entities()

        self.sections = sections

        # list of snapshots
        self.graph_sequence = [] 

        # list of list of matches
        self.matches_sequence = []
        self.doc_lengths_sequence = []

        self.data_path = data_path

        # either load from saved state or regenerate.
        state_changed = self.restore_state(force_reload)

        # save if state changed.
        if autosave and state_changed:
            self.save()

    def restore_state(self, force_reload):
        regenerate = 'all' if force_reload else self.should_regenerate()
        if regenerate == 'none':
            self.load()
            state_changed = False
        else:
            if regenerate == 'all':
                self.process_book()
            elif regenerate == 'edges':
                self.load_matches()
                for section_number in self.sections:
                    self.create_section_graph(section_number)
            state_changed = True
        return state_changed

    def process_book(self):
        for section_number in self.sections:
            print("+-------------------------------------")
            print("| Processing section " + str(section_number))
            print("+-------------------------------------")
            section_text = text_io.interpolate_section_endnotes(text_io.get_section(section_number))

            result = ner.recognize_text(section_text, print_results=DEBUG)

            self.doc_lengths_sequence.append(result['text_length'])
            self.matches_sequence.append(result['matches'])
            self.create_section_graph(section_number)

    def create_section_graph(self, section_number):
        section_index = section_number - 1
        matches = self.matches_sequence[section_index]
        section_length = self.doc_lengths_sequence[section_index]

        # 1. recognize entities
        added_V = self.make_nodes(matches)
        # 2. link entities.
        added_E = self.make_edges(matches)
        # 3. graph.
        snapshot = GraphSnapshot(V=added_V, E=added_E, section=section_number, section_length=section_length)

        self.graph_sequence.append(snapshot)

    def make_nodes(self, matches):
        print_debug(1, "NODES:")
        section_people = set([match.key for match in matches])
        new_people = section_people - self.people
        # keep node ids in same order each run by sorting here.
        for key in sorted(list(new_people)):
            self.people.add(key)
            print_debug(1, "  New node: ({})".format(key))

            add_node_attributes(self.G, self.entities, key)
        return section_people

    def graph_by_sections(self, sequence, aggregate=False, decay_weights=False, stability=10):
        g0 = GraphSnapshot()
        for section_num in sequence:
            section_snapshot = self.graph_sequence[section_num-1]
            if aggregate:
                if decay_weights:
                    scale = self.forgetting_curve(section_snapshot.section_length, S=stability)
                    self.decay_weights(g0.E, scale)
                g0 = g0.merge(section_snapshot)
                yield g0.getNXGraph()
            else:
                yield section_snapshot.getNXGraph()

    def decay_weights(self, edges, scale):
        for k1, innerdict in edges.items():
            for k2, v in innerdict.items():
                edges[k1][k2] = (v * scale)

    def forgetting_curve(self, length, S=2):
        return math.e**(-1 * length / (10000*S))

    def add_edge_from_matches(self, first, second):
        if first.key == second.key:
            print_debug(3, "  - Skipped match b/c same entity")
            return False

        if first.start > second.start:
            first, second = second, first

        if second.start - first.start > self.edge_threshold:
            print_debug(3, "  - Skipped match b/c outside edge thresh")
            return False

        if self.G.has_edge(first.key, second.key):
            self.G[first.key][second.key]['weight'] += 1
        else:
            self.G.add_edge(first.key, second.key, weight=1)
        if DEBUG > 1:
            print("  - Incr weight ({},{}), pos=({},{})".format(
                first.key, second.key,
                first.start, second.start))
        return True

    def make_edges(self, matches):
        # dict for counting weights
        new_edges = defaultdict(lambda: defaultdict(int))
        # dict for tracking edge thresholds for smoothing.
        # heuristic to avoid multi-counting
        edge_block_threshs = defaultdict(lambda: defaultdict(int))
        # dumbest way possible: link if within THRESHOLD tokens of eachother.
        # note: this adds 1 edges per match pair, only in one direction.
        for i, first in enumerate(matches[:-1]):
            for second in matches[i + 1:]:
                print_debug(3, "[Process match:{}, {}]".format(str(first), str(second)))
                if first.key > second.key:
                    first, second = second, first
                match_start = min(first.start, second.start)
                match_end = max(first.end, second.end)
                if match_start > edge_block_threshs[first.key][second.key]:
                    # don't add a new edge if we're within the blocking 
                    # threshold from the previous edge.
                    new_edge = self.add_edge_from_matches(first, second)
                    if new_edge:
                        new_edges[first.key][second.key] += 1
                        edge_block_threshs[first.key][second.key] = match_end + self.edge_repeat_threshold
                else:
                    print_debug(3, "  - Skipped match b/c within thresh ({})"
                        .format(edge_block_threshs[first.key][second.key]))
        print_debug(1, "EDGES:")
        for key1, inner_dict in new_edges.items():
            for key2, weight in inner_dict.items():
                print_debug(1, "  {} <--> {}, weight:+{}".format(key1, key2, weight))
        return new_edges

    def save(self):
        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)

        # write aggregate list of vertices (keys + ids) to file
        with open(self.aggregate_nodes_path, 'w') as f:
            for i, key in enumerate(self.people):
                f.write("{}\t{}\n".format(i, key))
        # write complete graph
        nx.write_weighted_edgelist(self.G, self.aggregate_edgelist_path)

        # write each section snapshot to file
        sect_path = self.data_path + '/sections'

        if not os.path.exists(self.sections_path):
            os.mkdir(self.sections_path)

        # write each snapshot to a file
        for snap in self.graph_sequence:
            snap.save(self.sections_path)

        # save entities hash to later determine if we need to rerun
        with open(self.cached_state_path, 'w') as f:
            json.dump(self.cache_info, f)

        # save the entity matches
        if not os.path.exists(self.matches_path):
            os.mkdir(self.matches_path)

        for i in self.sections:
            matches = self.matches_sequence[i - 1]
            with open(self.get_section_matches_path(i), 'w') as f:
                json.dump(matches, f)

        with open(self.document_lengths_path, 'w') as f:
            json.dump(self.doc_lengths_sequence, f)

    @property
    def cache_info(self):
        return {
            'edge_threshold' : self.edge_threshold,
            'edge_repeat_threshold' : self.edge_repeat_threshold,
            'entities_hash' : get_entities_hash(),
        }

    @property
    def sections_path(self):
        return os.path.join(self.data_path, 'sections')

    @property
    def aggregate_nodes_path(self):
        return os.path.join(self.data_path, 'aggregate_nodes.txt')

    @property
    def aggregate_edgelist_path(self):
        return os.path.join(self.data_path, 'aggregate_edgelist.txt')

    @property
    def cached_state_path(self):
        return os.path.join(self.data_path, 'cached_state_path.json')

    @property
    def matches_path(self):
        return os.path.join(self.data_path, 'matches')

    @property
    def document_lengths_path(self):
        return os.path.join(self.matches_path, 'document_lengths.json')

    def get_section_matches_path(self, section_number):
        return os.path.join(self.matches_path, str(section_number) + '-matches.json')

    def should_regenerate(self):
        """ there are two types of regenerations, 
        1. 'all' - where the entities have changed
        2. 'edges' - where the edges have changed
        (we can also not need to reload at all)
        """
        if not os.path.exists(self.cached_state_path):
            return 'all'

        with open(self.cached_state_path, 'r') as f:
            old_cache_info = json.load(f)

        if old_cache_info['entities_hash'] != self.cache_info['entities_hash']:
            return 'all'
        else:
            for key, value in self.cache_info.items():
                if old_cache_info[key] != value:
                    return 'edges'

            return 'none'

        return 'all'

    def load(self):
        # load graph from edgelist
        # load vertices
        self.G = nx.read_edgelist(self.aggregate_edgelist_path, nodetype=str, data=(('weight', int),))
        with open(self.aggregate_nodes_path, 'r') as f:
            for line in f:
                node_id, key = line.split()
                add_node_attributes(self.G, self.entities, key)

                if key not in self.people:
                    self.people.add(key)

        self.graph_sequence = []
        for i in self.sections:
            snap = GraphSnapshot(section=i)
            snap.load(self.sections_path)
            self.graph_sequence.append(snap)

        self.load_matches()

    def load_matches(self):
        for i in self.sections:
            with open(self.get_section_matches_path(i), 'r') as f:
                matches = json.load(f)

            self.matches_sequence.append([ner.Match(**match) for match in matches])

        with open(self.document_lengths_path, 'r') as f:
            self.doc_lengths_sequence = json.load(f)


if __name__ == "__main__":
    # build a graph per section.
    gg = Graphify()
