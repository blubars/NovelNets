#! /usr/bin/env python3
#########################################################
# File Description:
#   Make plots for analysis
# Date: 11/16/18
#########################################################
import json
import os
import csv
import analyze
import argparse
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd

from collections import defaultdict

ANALYSIS_PATH = '../data/analysis/'
PLOTS_PATH = '../data/plots/'

#########################################################
# Function definitions
#########################################################
def plot_ccdf(deg_seq, outfile):
    bins = [k+1 for k in range(max(deg_seq)+1)]
    cumbins = [0 for k in range(max(deg_seq)+1)]
    for k in deg_seq:
        cumbins[k] += 1
    for i in range(len(cumbins)-2, -1, -1):
        cumbins[i] = (cumbins[i+1] + cumbins[i])
    for i in range(len(cumbins)):
        cumbins[i] /= len(cumbins)
    fig = plt.figure(1)
    plt.loglog(bins, cumbins)
    plt.title("Degree Distribution CCDF")
    plt.xlabel("Degree, $k$")
    plt.ylabel("CCDF P($x \geq X$)")
    plt.tight_layout()
    plt.savefig(outfile)
    plt.close(fig)

def plot_df(df, x_name, y_name, title, logx=False):
    fig = plt.figure(1)
    X = df[x_name]
    Y = df[y_name]
    plt.plot(X, Y)
    plt.title(title)
    plt.ylabel(y_name.title())
    plt.xlabel(x_name.title())
    if logx:
        plt.xscale('log')
    plt.tight_layout()
    fname = x_name.lower() + '_vs_' + y_name.lower() + ".png"
    fname = fname.replace(" ", "_")
    plt.savefig(os.path.join(PLOTS_PATH, fname))
    plt.close(fig)

def make_plots():
    print("Saving plots to '{}'".format(ANALYSIS_PATH))
    df = pd.read_csv(ANALYSIS_PATH + 'geodesic_vs_degree.csv')
    plot_df(df, "avg degree", "avg geodesic len", "Attachment: Degree vs Avg Geodesic Path, By Section")
    plot_df(df, "n", "avg geodesic len", "Attachment: Log(n) vs Avg Geodesic Path", logx=True)
    df = pd.read_csv(ANALYSIS_PATH + 'edge_dist_analysis.csv')
    plot_df(df, "thresh", "GC size", "Threshold choice: Giant Component Size")
    plot_df(df, "thresh", "avg clustering", "Threshold choice: Clustering Coefficient")
    plot_df(df, "thresh", "mean weighted degree", "Threshold choice: Weighted Mean Degree")

def plot_neighborhood_stabilities():
    1

def section_bars():
    chronological = analyze.get_section_sequence(chronological=True)
    booktime = analyze.get_section_sequence(chronological=False)

    # Make a figure and axes with dimensions as desired.
    fig = plt.figure(figsize=(8, 3))
    ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.15])
    ax2 = fig.add_axes([0.05, 0.475, 0.9, 0.15])

    rainbow = matplotlib.cm.rainbow(np.linspace(0, 1, 192))
    norm = matplotlib.colors.Normalize(vmin=1, vmax=192)
    bounds = [1, 192]

    booktime = [None for _ in range(len(chronological))]
    new_chronological = [i + 1 for i in range(len(chronological))]
    for book, chrono in enumerate(chronological):
        booktime[chrono - 1] = book + 1

    chronological_colormap = [rainbow[i - 1] for i in new_chronological]

    cb1 = matplotlib.colorbar.ColorbarBase(
        ax1,
        cmap=matplotlib.colors.ListedColormap(chronological_colormap),
        norm=norm,
        orientation='horizontal',
        ticks=bounds,
    )
    cb1.set_label('chronological ordering')

    booktime_colormap = [rainbow[i - 1] for i in booktime]

    cb2 = matplotlib.colorbar.ColorbarBase(
        ax2,
        cmap=matplotlib.colors.ListedColormap(booktime_colormap),
        norm=norm,
        orientation='horizontal',
        ticks=bounds,
    )
    cb2.set_label('book ordering')

    plt.savefig(os.path.join(PLOTS_PATH, 'section_bars.png'))
    plt.show()
    plt.close(fig)


def get_dynamics(chronological=True, weighted=True):
    data_file_name = "dynamics-chronological_{}-weighted_{}.csv".format(chronological, weighted)
    data_path = os.path.join(ANALYSIS_PATH, data_file_name)

    if not os.path.exists(data_path):
        print('no data!')
        return

    with open(data_path, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=',')

        rows = []
        header = None
        for i, row in enumerate(reader):
            if i == 0:
                header = row
            else:
                row_dict = { header[key] : val for key, val in enumerate(row)}
                row_dict['index'] = i - 1
                rows.append(row_dict)
    return rows

def plot_dynamic(dynamic, booktime_data, chronological_data, yscale=None):
    xs = [r['index'] for r in booktime_data]
    chronological_avg_degrees = [float(r[dynamic]) for r in chronological_data]
    booktime_avg_degrees = [float(r[dynamic]) for r in booktime_data]

    fig = plt.figure(1)
    plt.plot(chronological_avg_degrees, label='chronological')
    plt.plot(booktime_avg_degrees, label='booktime')
    plt.title("{} by section, chronological and booktime".format(dynamic))
    plt.ylabel('{}'.format(dynamic))
    plt.xlabel('section index')

    if yscale:
        plt.yscale(yscale)

    plt.xlim(0, 192)
    plt.legend()
    plt.tight_layout()

    fname = "dynamics-{}.png".format(dynamic)
    plt.savefig(os.path.join(PLOTS_PATH, fname))
    plt.close(fig)

def plot_dynamics():
    booktime_rows = get_dynamics(chronological=False)
    chronological_rows = get_dynamics(chronological=True)
    plot_dynamic('avg degree', booktime_rows, chronological_rows)
    plot_dynamic('avg geodesic len', booktime_rows, chronological_rows)
    plot_dynamic('num components', booktime_rows, chronological_rows)
    plot_dynamic('largest component size', booktime_rows, chronological_rows)
    plot_dynamic('n', booktime_rows, chronological_rows)

def get_neighborhood_scene_stabilities(chronological):
    with open(os.path.join(ANALYSIS_PATH, 'neighborhood_stabilities-chronological_{}.json'.format(chronological)), 'r') as f:
        stabilities = json.load(f)

    scene_stabilities = defaultdict(list)

    for entity, stability_vals in stabilities.items():
        for stability_val in stability_vals:
            scene = stability_val[1]
            stability = float(stability_val[2])

            scene_stabilities[scene].append(stability)

    avg_scene_stabilities = [0 for _ in range(1, 193)]
    for scene, scene_stabilities in scene_stabilities.items():
        avg_scene_stabilities[scene] = sum(scene_stabilities) / len(scene_stabilities)

    return avg_scene_stabilities

def plot_neighborhoods():
    chronological_scene_stabilities = get_neighborhood_scene_stabilities(True)
    booktime_scene_stabilities = get_neighborhood_scene_stabilities(False)

    fig = plt.figure(1)
    plt.plot(chronological_scene_stabilities, label='chronological')
    plt.plot(booktime_scene_stabilities, label='booktime')
    plt.title("neighborhood stability by entity")
    plt.ylabel("neighborhood stability")
    plt.xlabel("scene index")
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.savefig(os.path.join(PLOTS_PATH, 'neighborhood.png'))
    plt.close(fig)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Plot Infinite Jest")
    parser.add_argument('--section_bars', '-s', default=False, action="store_true", help="create the section bars")
    parser.add_argument('--make_plots', '-p', help="Make plots", action="store_true")
    parser.add_argument('--dynamics', '-d', help="plot dynamics", action="store_true")
    parser.add_argument('--neighborhoods', '-n', help="plot dynamics", action="store_true")

    args = parser.parse_args()

    if args.section_bars:
        section_bars()

    if args.dynamics:
        plot_dynamics()

    if args.neighborhoods:
        plot_neighborhoods()
