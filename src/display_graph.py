from webweb.webweb import webweb
import argparse

from graphify import Graphify
import infinite_jest_utils

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--chronological', '-c', default=False, action="store_true", help="chronological or book time")

    args = parser.parse_args()

    gg = Graphify(edge_thresh=50)

    web = webweb()
    web.display.colorBy = 'degree'
    web.display.sizeBy = 'degree'
    web.display.l = 60
    web.display.c = 120
    web.display.scaleLinkWidth = True
    # web.display.w = 600
    # web.display.h = 600

    section_sequence = infinite_jest_utils.get_section_sequence(chronological=False)
    for G in gg.graph_by_sections(section_sequence, aggregate=True, decay_weights=True, stability=40):
        web.networks.infinite_jest.add_frame_from_networkx_graph(G)

    section_sequence = infinite_jest_utils.get_section_sequence(chronological=True)
    for G in gg.graph_by_sections(section_sequence, aggregate=True, decay_weights=True, stability=40):
        web.networks.infinite_jest_chronological.add_frame_from_networkx_graph(G)

    web.draw()
