#!/usr/bin/env python
# coding: utf-8

# In[1]:

import os
import pandas as pd
import numpy as np
import holoviews as hv
from holoviews import opts, dim
from bokeh.plotting import figure
from bokeh.embed import components

import void

def build_layout(datadir):
    hv.extension('bokeh')
    hv.output(size=600)

    # Read file Immigrazione
    dfi = pd.read_csv(os.path.join(datadir, 'apr_Noventa_fix.csv'))

    # Read file Emigrazione
    dfe = pd.read_csv(os.path.join(datadir, 'emigrazione_Noventa_fix.csv'))

    # Cancella campi con CANC.
    dfe = dfe[~dfe['LuogoEmigrazione'].str.contains('CANC.')]

    # Aggregate and count
    gi = dfi.groupby('COMUNE PROVENIENZA').size().reset_index(name='Flusso')
    ge = dfe.groupby('LuogoEmigrazione').size().reset_index(name='Flusso')

    # Add Origin(Destination Link
    gi['Destinazione'] = 'NOVENTA DI PIAVE'
    ge['Origine'] = 'NOVENTA DI PIAVE'

    # Concat dataframes
    gi.columns = ['Origine','Flusso','Destinazione']
    ge.columns = ['Destinazione','Flusso','Origine']
    g = pd.concat([gi, ge], ignore_index=True)

    # Filter flow
    g = g.sort_values(by=['Flusso'], ascending=False)
    g = g[(g['Flusso']>=100)]

    # Format
    links = g[['Origine','Destinazione','Flusso']]

    # Color
    chord = hv.Chord(links)

    # Colormap VOID
    cmap = ['#f6b700','#2d2926','#489fdf','#2cc84d','#ee3831','#e5cde6','#ffff66','#336699','#808080']

    chord.opts(
        opts.Chord(cmap=cmap,
                edge_cmap=cmap,
                edge_color='Origine',
                node_color='index',
                label_index='index',
                frame_width=100, frame_height=100))


    # Save Interactive image only
    renderer = hv.renderer('bokeh')

    return renderer.get_plot_state(chord)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--datadir', type=str, required=True)
    parser.add_argument('--htmlfile', type=str, required=True)

    args = parser.parse_args()

    outf = args.htmlfile
    datadir = args.datadir

    layout = build_layout(datadir)

    void.setup_fonts(layout)

    script, div = components(layout)


    with open('template.html', 'r') as ftempl:
        htmltempl = ftempl.read()

#        script, div = components(layout)
        htmltempl = htmltempl.replace('$BOKEH_DIV$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT$', script)

        with open(outf, 'w') as fout:
            fout.write(htmltempl)


