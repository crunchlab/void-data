#!/usr/bin/env python
# coding: utf-8
# pip install bokeh

import void

from datetime import timedelta
import os

import numpy as np
import pandas as pd

from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource
from bokeh.palettes import small_palettes
from bokeh.models import Legend
from bokeh.layouts import row, column
from bokeh.embed import components
from bokeh.models import CheckboxGroup, Button

from bokeh.models.callbacks import CustomJS

def affluenza(datadir):
    df = pd.read_csv(os.path.join(datadir, 'ConsultazioniElettoraliReferendum.csv'),
                     sep=';', parse_dates=["Data"])
    # % votanti femmine/maschi su totale votanti
    df['PvF'] = df['Votanti_femmine']/df['Totale_votanti']*100
    df['PvM'] = df['Votanti_maschi']/df['Totale_votanti']*100

    # Affluenza
    df['Affluenza'] = df['Totale_votanti']/df['Totale_Elettori']*100

    # Sostituisci tutte le forme di Referendum con Referendum generico
    df = df.replace(['Referendum Popolare','Referendum Confermativo', 'Referendum consultivo'],'Referendum')

    # Raggruppa per Anno e Consultazione e prendi la media delle affluenze
    g = df.groupby(['Anno','Consultazione'])['Affluenza'].mean().reset_index()

    # PLOT

    mask_politiche = g['Consultazione'] == 'Elezioni Politiche'
    mask_cost = g['Consultazione'] == 'Assemblea Costituente'
    mask_ammin = g['Consultazione'] == 'Elezioni Amministrative'
    mask_refer = g['Consultazione'] == 'Referendum'

    masks = [mask_politiche, mask_cost, mask_ammin, mask_refer]
    colors = [void.color_table['yellow'],
            void.color_table['gray'],
            void.color_table['green'],
            void.color_table['red'],
    ]
    labels = ['Elezioni Politiche',
            'Assemblea Costituente',
            'Elezioni Amministrative',
            'Referendum']

    p = figure(plot_width=800, plot_height=400,
            title="AFFLUENZA")

    rad = 0.5
    line_color = None

    for l, c in zip(labels, colors):
        m = g['Consultazione'] == l
        x = g[m]['Anno']
        y = g[m]['Affluenza']

        p.circle(x, y, fill_color=c, legend_label=l, line_color=line_color, radius=rad)

    p.xaxis.axis_label = 'Anno'
    p.yaxis.axis_label = 'Affluenza (%)'
    p.legend.location = (0,0)

    void.setup_fonts(p)

    # CALLBACKS
    checkbox_cb = CustomJS(args=dict(renderers=p.renderers), code = """
    renderers.forEach(r => {
        r.visible = false;
    });
    this.active.forEach(a => {
        renderers[a].visible = true;
    });
    """)
    checkbox_group = CheckboxGroup(labels=labels, active=[0, 1, 2, 3])
    checkbox_group.js_on_click(checkbox_cb)

    layout = column(p, checkbox_group)

    return layout

def gender(datadir):
    g = pd.read_csv(os.path.join(datadir,'dfs.csv'))

    # PLOT
    mask_politiche = g['Consultazione'] == 'Elezioni Politiche'
    mask_cost = g['Consultazione'] == 'Assemblea Costituente'
    mask_ammin = g['Consultazione'] == 'Elezioni Amministrative'
    mask_refer = g['Consultazione'] == 'Referendum'

    masks = [mask_politiche, mask_cost, mask_ammin, mask_refer]
    colors = [void.color_table['yellow'],
            void.color_table['gray'],
            void.color_table['green'],
            void.color_table['red'],
    ]
    labels = ['Elezioni Politiche',
            'Assemblea Costituente',
            'Elezioni Amministrative',
            'Referendum']

    p = figure(plot_width=800, plot_height=400,
            title="TIPOLOGIA DI ELETTORATO")

    rad = 0.05
    line_color = None
    alpha=0.5

    for l, c in zip(labels, colors):
        m = g['Consultazione'] == l
        x = g[m]['PvM']
        y = g[m]['PvF']

        p.circle(x, y, fill_color=c, legend_label=l,
                line_color=line_color, radius=rad, fill_alpha=alpha)

    p.xaxis.axis_label = '% Votanti Maschi'
    p.yaxis.axis_label = '% Votanti Femmine'
    p.legend.location = (0,0)

    void.setup_fonts(p)

    # CALLBACKS
    checkbox_cb = CustomJS(args=dict(renderers=p.renderers), code = """
    renderers.forEach(r => {
        r.visible = false;
    });
    this.active.forEach(a => {
        renderers[a].visible = true;
    });
    """)
    checkbox_group = CheckboxGroup(labels=labels, active=[0, 1, 2, 3])
    checkbox_group.js_on_click(checkbox_cb)

    cb_code = """
    renderers.forEach(r => {
        r.glyph.radius = Math.max(0.01, r.glyph.radius.value + delta);
    });
    """

    cb_less = CustomJS(args=dict(renderers=p.renderers, delta=0.01), code=cb_code)
    cb_more = CustomJS(args=dict(renderers=p.renderers, delta=-0.01), code=cb_code)

    btn_less = Button(label="ALLARGA", button_type="success")
    btn_less.js_on_click(cb_less)
    btn_more = Button(label="RIDUCI", button_type="danger")
    btn_more.js_on_click(cb_more)

    # OUTPUT

    actions = row(checkbox_group, column(btn_more, btn_less))
    layout = column(p, actions)

    return layout



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--datadir', type=str, required=True)
    parser.add_argument('--htmlfile', type=str, required=True)

    args = parser.parse_args()

    outf = args.htmlfile
    datadir = args.datadir

    with open('template.html', 'r') as ftempl:
        htmltempl = ftempl.read()

        script, div = components(affluenza(datadir))
        htmltempl = htmltempl.replace('$BOKEH_DIV_1$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_1$', script)

        script, div = components(gender(datadir))
        htmltempl = htmltempl.replace('$BOKEH_DIV_2$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_2$', script)

        with open(outf, 'w') as fout:
            fout.write(htmltempl)

