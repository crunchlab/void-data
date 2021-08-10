print("Loading libraries...")

import os
import argparse

import pandas as pd
import numpy as np
import glob
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import community
from bokeh.plotting import figure, from_networkx
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, EdgesAndLinkedNodes, NodesAndLinkedEdges, LabelSet
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.io import output_notebook, show, save
from bokeh.transform import linear_cmap

from bokeh.embed import components

import void

def build_layout(data_dir):

    data_path = os.path.join(data_dir, "*.csv")
    print("Building the network...")
    # Read files
    df = pd.concat(map(pd.read_csv, glob.glob(data_path)))
    # Filter Provincia di Provenienza Veneto
    df = df[df['PROVINCIA_PROVENIENZA'].isin(['VE','TV','PD','VR','BL','RO','VI'])]
    # Add weight to links
    df['weight'] = df.groupby(['COMUNE_PROVENIENZA', 'COMUNE'])['COMUNE_PROVENIENZA'].transform('size')
    # Drop Duplicates
    df = df.drop_duplicates(subset=['COMUNE','COMUNE_PROVENIENZA','weight'])
    # Filter network with more than 50 movements
    df = df[df['weight']>=50]
    # Drop nan
    df = df.dropna(subset=['COMUNE','COMUNE_PROVENIENZA','weight'])

    # Build network
    G = nx.from_pandas_edgelist(df, 'COMUNE_PROVENIENZA', 'COMUNE', create_using=nx.DiGraph(), edge_attr='weight')

    degrees = dict(nx.degree(G))
    nx.set_node_attributes(G, name='degree', values=degrees)

    # Slightly adjust degree so that the nodes with very small degrees are still visible
    number_to_adjust_by = 3
    adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in nx.degree(G)])
    nx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)

    print("Creating the plot...")

    # Choose colors for node and edge highlighting
    node_highlight_color = 'white'
    edge_highlight_color = 'black'

    # Choose attributes from G network to size and color by — setting manual size (e.g. 10) or color (e.g. 'skyblue') also allowed
    size_by_this_attribute = 'adjusted_node_size'
    color_by_this_attribute = 'adjusted_node_size'

    # Pick a color palette — Blues8, Reds8, Purples8, Oranges8, Viridis8
#    color_palette = Blues8
    color_palette = void.palette5

    # Choose a title!
    title = 'Rete delle Migrazioni dal 2000 al 2020'

    # Establish which categories will appear when hovering over each node
    HOVER_TOOLTIPS = [("Comune", "@index"),("Migrazioni", "@degree")]

    # Create a plot — set dimensions, toolbar, and title
    plot = figure(tooltips = HOVER_TOOLTIPS,
                  plot_width=800, plot_height=800,
                  tools="pan,wheel_zoom,save,reset",
                  active_scroll='wheel_zoom',
                  title=title)

    # Hide Axes
    plot.axis.visible = False

    # Create a network graph object
    # https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html
    network_graph = from_networkx(G, nx.circular_layout, scale=10, center=(0, 0))

    #Set node sizes and colors according to node degree (color as spectrum of color palette)
    minimum_value_color = min(network_graph.node_renderer.data_source.data[color_by_this_attribute])
    maximum_value_color = max(network_graph.node_renderer.data_source.data[color_by_this_attribute])
    network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=linear_cmap(color_by_this_attribute, color_palette, minimum_value_color, maximum_value_color))

    #Set node highlight colors
    network_graph.node_renderer.hover_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
    network_graph.node_renderer.selection_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)

    # Set edge opacity and width
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)

    # Set edge highlight colors
    network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
    network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)

    # Highlight nodes and edges
    network_graph.selection_policy = NodesAndLinkedEdges()
    network_graph.inspection_policy = NodesAndLinkedEdges()

    # Add Labels
    x, y = zip(*network_graph.layout_provider.graph_layout.values())
    node_labels = list(G.nodes())
    source = ColumnDataSource({'x': x, 'y': y, 'name': [node_labels[i] for i in range(len(x))]})
    labels = LabelSet(x='x', y='y', text='name', source=source, background_fill_color='white', text_font_size='8px', background_fill_alpha=.7)
    plot.renderers.append(labels)

    plot.renderers.append(network_graph)

    return plot

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--datadir', type=str, required=True)
    parser.add_argument('--htmlfile', type=str, required=True)

    args = parser.parse_args()

    outf = args.htmlfile
    datadir = args.datadir

    layout = build_layout(datadir)
    void.setup_fonts(layout)

    with open('template.html', 'r') as ftempl:
        htmltempl = ftempl.read()

        script, div = components(layout)
        htmltempl = htmltempl.replace('$BOKEH_DIV$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT$', script)

        with open(outf, 'w') as fout:
            fout.write(htmltempl)

