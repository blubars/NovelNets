#! /usr/bin/env python3
#########################################################
# File Description:
#   Make plots for analysis
# Date: 11/16/18
#########################################################
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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

def plot_df(df, x_name, y_name, title, logx=False, path=""):
    fig = plt.figure(1)
    X = df[x_name]
    Y = df[y_name]
    plt.scatter(X, Y)
    plt.plot(X, Y)
    plt.title(title)
    plt.ylabel(y_name.title())
    plt.xlabel(x_name.title())
    if logx:
        plt.xscale('log')
    plt.tight_layout()
    fname = x_name.lower() + '_vs_' + y_name.lower() + ".png"
    fname = fname.replace(" ", "_")
    plt.savefig(path + fname)
    plt.close(fig)

def make_plots(analysis_path):
    print("Saving plots to '{}'".format(analysis_path))
    df = pd.read_csv(analysis_path + 'geodesic_vs_degree.csv', encoding="utf-8")
    plot_df(df, "avg degree", "avg geodesic len", "Attachment: Degree vs Avg Geodesic Path, By Section", path=analysis_path)
    plot_df(df, "n", "avg geodesic len", "Attachment: Log(n) vs Avg Geodesic Path", logx=True, path=analysis_path)
    df = pd.read_csv(analysis_path + 'edge_dist_analysis.csv', encoding="utf-8")
    plot_df(df, "thresh", "GC size", "Threshold choice: Giant Component Size", path=analysis_path)
    plot_df(df, "thresh", "avg clustering", "Threshold choice: Clustering Coefficient", path=analysis_path)
    plot_df(df, "thresh", "mean weighted degree", "Threshold choice: Weighted Mean Degree", path=analysis_path)

