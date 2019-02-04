#! /usr/bin/env python3

#########################################################
# File Description:
#   Main entry point to coherent program. Turn a book
#   into a graph.
# Authors: Brian Lubars, Hunter Wapman, Carl Mueller
# Date: 02/01/19
#########################################################
import os
import re
import sys
import argparse

from graphify import Graphify
from text_io import TextIOReader
from entities import EntityIO, run_entity_processing
from display_graph import display_with_webweb

class BookProcesser:
    def __init__(self, book_path, book_title=None, preprocess_path=None, graph_path=None):
        #self.base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..")
        self.base_path = "."
        self.raw_book_path = book_path
        self.preprocess_path = preprocess_path
        self.graph_path = graph_path
        self.set_book_title(book_title)

        book_dir_name = self.pathify_book_name()
        if not preprocess_path:
            self.preprocess_path = os.path.join(self.base_path, "preprocess", book_dir_name)
        if not graph_path:
            self.graph_path = os.path.join(self.base_path, "graphs", book_dir_name)
        self.prep_dir(self.preprocess_path)
        self.prep_dir(self.graph_path)

        self.textIO = TextIOReader(self.get_section_path())
        self.entityIO = EntityIO(self.preprocess_path)

        print("Creating Graph!")
        print(" -- Using book: {}".format(self.raw_book_path))
        print(" -- Book title: {}".format(self.get_book_title()))
        print(" -- Using preprocess dir: {}".format(self.preprocess_path))
        print(" -- Using graph cache dir: {}".format(self.graph_path))
        print()

    def prep_dir(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def run(self):
        # do all the steps.
        self.preprocess()
        self.run_interactive_entity_disambiguation()
        self.graphify()
        self.analyze()
        self.display()

    def set_book_title(self, title=None):
        """ Set book name from book file path """
        if title is None:
            fname = os.path.basename(self.raw_book_path)
            title = os.path.splitext(fname)[0]
        self.title = title

    def get_book_title(self):
        """ Get book title """
        return self.title

    def pathify_book_name(self):
        """ Turn a book name/title/filename into a directory """
        title = self.get_book_title()
        dir_name = title.lower()
        dir_name = re.sub(r' ', r'-', dir_name)
        dir_name = re.sub(r'[^\x61-\x7A-]', r'', dir_name)
        return dir_name

    def get_section_path(self):
        """ Get section directory relative to base """
        return os.path.join(self.preprocess_path, "sections/")

    def enumerate_sections(self, section_dir):
        sections = []
        for entry in os.scandir(section_dir):
            if not entry.name.startswith('.') and entry.is_file():
                m = re.search(r'\d+', entry.name)
                sections.append(int(m.group(0)))
        return sorted(sections)

    def preprocess(self):
        """ Check if book is split into sections; do it if not. """
        print("+-------------------------------------")
        print("| Book text pre-processing")
        print("+-------------------------------------")
        # is book already split into sections?
        section_dir = self.get_section_path()
        print(section_dir)
        if os.path.isdir(section_dir):
            # already pre-processed.
            self.sections = self.enumerate_sections(section_dir)
            print("Found {} sections.".format(len(self.sections)))
        else:
            # do pre-processing. split into sections (TODO).
            print("Error: Book must be split into sections.")
            sys.exit(1)

    def run_interactive_entity_disambiguation(self):
        print("+-------------------------------------")
        print("| Named Entity Processing")
        print("+-------------------------------------")
        if not self.entityIO.entity_file_exists():
            print("Could not find entities file. Generating new one!")
            section_path = self.get_section_path()
            run_entity_processing(self.entityIO, self.textIO, self.sections, True)
        else:
            print("Found existing entities file: {}".format(self.entityIO.get_entities_path()))
            # TODO: check which sections have been done; process
            # only missing sections.
            print(f"Do you want to update the list of recognized entities?\n'y' to find new entities, 'n' to run graphify with existing entities.\n (Enter y/N)")
            answer = input()
            if answer == 'y':
                section_path = self.get_section_path()
                run_entity_processing(self.entityIO, self.textIO, self.sections, True)

    def graphify(self):
        print("+-------------------------------------")
        print("| Building graph from \"{}\"".format(self.get_book_title()))
        print("+-------------------------------------")
        self.graph = Graphify(self.textIO, self.entityIO, data_path=self.graph_path, sections=self.sections)
        print("Done!")

    def analyze(self):
        print("+-------------------------------------")
        print("| Network Analysis")
        print("+-------------------------------------")
        print("Interactive analysis not implemented. Please use analyze.py")

    def display(self):
        print("+-------------------------------------")
        print("| Displaying Network")
        print("+-------------------------------------")
        display_with_webweb(self.graph, self.sections)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turn a book into a graph!")
    parser.add_argument('--book', '-b', help="Location of book. Raw txt/mobi.", default=None)
    parser.add_argument('--title', '-t', help="Title of book. If omitted, will be inferred from book file name", default=None)
    parser.add_argument('--preprocess_dir', '-p', help="Location of preprocessed book. Should contain a sections dir, with book split into individual sections", default=None)
    parser.add_argument('--save_dir', '-s', help="Directory to save cache & output data", default=None)

    args = parser.parse_args()
    if args.book is None:
        if args.title is None:
            print("Error: please include either book or title argument")
            sys.exit(1)
        else:
            args.book = args.title

    reader = BookProcesser(
            book_path=args.book, 
            book_title=args.title, 
            preprocess_path=args.preprocess_dir,
            graph_path=args.save_dir)
    reader.run()

