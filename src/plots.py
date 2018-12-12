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

def plot_attachment():
    try:
        df = pd.read_csv(ANALYSIS_PATH + 'geodesic_vs_degree.csv')
        plot_df(df, "avg degree", "avg geodesic len", "Attachment: Degree vs Avg Geodesic Path, By Section")
        plot_df(df, "n", "avg geodesic len", "Attachment: Log(n) vs Avg Geodesic Path", logx=True)
    except:
        print("No data for attachment")

def plot_thresholds():
    try:
        df = pd.read_csv(ANALYSIS_PATH + 'edge_dist_analysis.csv')
        plot_df(df, "thresh", "GC size", "Threshold choice: Giant Component Size")
        plot_df(df, "thresh", "avg clustering", "Threshold choice: Clustering Coefficient")
        plot_df(df, "thresh", "mean weighted degree", "Threshold choice: Weighted Mean Degree")
    except:
        print("No data for thresholds")

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

def plot_dynamic(dynamic, weighted, booktime_data, chronological_data, yscale=None, ticks=None):
    chronological_ys = [float(r[dynamic]) for r in chronological_data]
    booktime_ys = [float(r[dynamic]) for r in booktime_data]

    fig = plt.figure(1)
    plt.plot(chronological_ys, label='chronological')
    plt.plot(booktime_ys, label='booktime')
    plt.title("{} by section, chronological and booktime".format(dynamic))
    plt.ylabel('{}'.format(dynamic))
    plt.xlabel('section index')

    if yscale:
        plt.yscale(yscale)

    if ticks == 'integer':
        ys = sorted(list(set([int(y) for y in chronological_ys + booktime_ys])))
        plt.yticks(ys)

    plt.xlim(0, 192)
    plt.legend()
    plt.tight_layout()

    fname = "dynamics-{}-weighted_{}.png".format(dynamic, weighted)
    plt.savefig(os.path.join(PLOTS_PATH, fname))
    plt.close(fig)

def plot_dynamics(weighted=False):
    booktime_rows = get_dynamics(chronological=False, weighted=False)
    chronological_rows = get_dynamics(chronological=True, weighted=False)

    plot_dynamic('avg degree', weighted, booktime_rows, chronological_rows)
    plot_dynamic('avg geodesic len', weighted, booktime_rows, chronological_rows)
    plot_dynamic('num components', weighted, booktime_rows, chronological_rows, ticks='integer')
    plot_dynamic('largest component size', weighted, booktime_rows, chronological_rows)
    plot_dynamic('n', weighted, booktime_rows, chronological_rows)

def plot_n_vs_geodesic(weighted=False):
    booktime_rows = get_dynamics(chronological=False, weighted=weighted)
    chronological_rows = get_dynamics(chronological=True, weighted=weighted)

    chronological_geodesic = [float(r['avg geodesic len']) for r in chronological_rows]
    chronological_n = [float(r['n']) for r in chronological_rows]

    booktime_geodesic = [float(r['avg geodesic len']) for r in booktime_rows]
    booktime_n = [float(r['n']) for r in booktime_rows]

    fig = plt.figure(1)
    plt.plot(chronological_n, chronological_geodesic, label='chronological')
    plt.plot(booktime_n, booktime_geodesic, label='booktime')
    plt.title("average geodesic by number of nodes, chronological and booktime")
    plt.ylabel('average geodesic path length')
    plt.xlabel('number of nodes')

    plt.legend()
    plt.tight_layout()

    fname = "n_vs_geodesic-weighted_{}".format(weighted)
    plt.savefig(os.path.join(PLOTS_PATH, fname))
    plt.close(fig)

def plot_n_vs_avg_degree(weighted=False):
    booktime_rows = get_dynamics(chronological=False, weighted=weighted)
    chronological_rows = get_dynamics(chronological=True, weighted=weighted)

    chronological_geodesic = [float(r['avg degree']) for r in chronological_rows]
    chronological_n = [float(r['n']) for r in chronological_rows]

    booktime_geodesic = [float(r['avg degree']) for r in booktime_rows]
    booktime_n = [float(r['n']) for r in booktime_rows]

    fig = plt.figure(1)
    plt.plot(chronological_n, chronological_geodesic, label='chronological')
    plt.plot(booktime_n, booktime_geodesic, label='booktime')
    plt.title("average degree by number of nodes, chronological and booktime")
    plt.ylabel('average degree')
    plt.xlabel('number of nodes')

    plt.legend()
    plt.tight_layout()

    fname = "n_vs_avg_degree-weighted_{}".format(weighted)
    plt.savefig(os.path.join(PLOTS_PATH, fname))
    plt.close(fig)

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

def plot_gender():
    with open(os.path.join(ANALYSIS_PATH, 'gender.json'), 'r') as f:
        content = json.load(f)

    n_groups = 2

    women = (content['unweighted']['female'], content['weighted']['female'])
    men = (content['unweighted']['male'], content['weighted']['male'])
    overall = (content['unweighted']['overall'], content['weighted']['overall'])

    fig, ax = plt.subplots()

    index = np.arange(n_groups)
    bar_width = 0.35

    opacity = 0.4
    error_config = {'ecolor': '0.3'}

    rects1 = ax.bar(index + index * bar_width, men, bar_width,
                    alpha=opacity, color='b',
                    error_kw=error_config,
                    label='male')

    rects2 = ax.bar(index + bar_width + (index * bar_width), overall, bar_width,
                    alpha=opacity, color='g',
                    error_kw=error_config,
                    label='overall')

    rects3 = ax.bar(index + 2 * bar_width +  (index * bar_width), women, bar_width,
                    alpha=opacity, color='r',
                    error_kw=error_config,
                    label='female')

    ax.set_xlabel('Group')
    ax.set_ylabel('average degree')
    ax.set_title('average degree by gender')
    ax.set_xticks(index + bar_width + (index * bar_width))
    ax.set_xticklabels(('unweighted', 'weighted'))
    ax.legend()

    fig.tight_layout()
    plt.savefig(os.path.join(PLOTS_PATH, 'gender.png'))


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
    plt.savefig(os.path.join(PLOTS_PATH, 'neighborhood.png'))
    plt.close(fig)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Plot Infinite Jest")
    parser.add_argument('--section_bars', '-s', default=False, action="store_true", help="create the section bars")
    parser.add_argument('--attachment', '-a', help="Plot attachment", action="store_true")
    parser.add_argument('--thresholds', '-t', help="Plot thresholds", action="store_true")
    parser.add_argument('--dynamics', '-d', help="plot dynamics", action="store_true")
    parser.add_argument('--neighborhoods', '-n', help="plot neighborhoods", action="store_true")
    parser.add_argument('--n_vs_geo', '-v', help="n vs geodesic", action="store_true")
    parser.add_argument('--n_vs_avg_degree', '-e', help="n vs avg degree", action="store_true")
    parser.add_argument('--gender', '-g', help="gender", action="store_true")

    args = parser.parse_args()
    print("Saving plots to '{}'".format(ANALYSIS_PATH))

    if args.attachment:
        plot_attachment()

    if args.thresholds:
        plot_thresholds()

    if args.section_bars:
        section_bars()

    if args.dynamics:
        plot_dynamics(weighted=False)

    if args.neighborhoods:
        plot_neighborhoods()

    if args.n_vs_geo:
        plot_n_vs_geodesic(weighted=False)

    if args.gender:
        plot_gender()

    if args.n_vs_avg_degree:
        plot_n_vs_avg_degree()
