#! /usr/bin/env python3

#########################################################
# File Description:
#   Run analysis on book
# Authors: Hunter Wapman, Brian Lubars, Carl Mueller
# Date: 12/1/18
#########################################################

#########################################################
# Imports
#########################################################
from graphify import Graphify

#########################################################
# Globals
#########################################################
SECTION_PATH = '../data/txt/sections/'
TOTAL_NUM_SECTIONS = 192

#########################################################
# Function definitions
#########################################################

def get_chronological_order():
    # read json files to extract chronological sect order
    pass

def graphify_whole_book(chronological=False):
    # build a graph per section.
    gg = Graphify(SECTION_PATH, 500, 50)
    sections = range(1,TOTAL_NUM_SECTIONS+1)
    gg.process_book(sections)
    return gg

if __name__ == "__main__":
    print("Analyzing book!")
    gg = graphify_whole_book()


