#!/usr/bin/env python
# coding: utf-8
# pip install bokeh

import void

from datetime import timedelta
import argparse

import numpy as np
import pandas as pd

from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource
from bokeh.palettes import small_palettes
from bokeh.models import Legend
from bokeh.layouts import row, column
from bokeh.models import HoverTool
from bokeh.embed import components

def build_layout(inf):
    # Deceduti

    # Import data
    #df = pd.read_csv('data/dataset.csv')
    df = pd.read_csv(inf)
    df['DataNascita'] = pd.to_datetime(df['DataNascita'], dayfirst=True)
    df['DataDecesso'] = pd.to_datetime(df['DataDecesso'], dayfirst=True)
    df = df.drop(['Cognome','Nome'],axis=1)

    # Calculate Age
    days = df['DataDecesso'] - df['DataNascita']
    years = days / np.timedelta64(1, 'Y')
    df['EtaDecesso'] = np.floor(years).astype('int')
    df.index = df['DataDecesso']

    # Remove 2021 (incomplete)
    df = df.drop(df.loc['2021'].index)

    # Fasce d'Eta'
    df['0_20'] = 0
    df['20_40'] = 0
    df['40_60'] = 0
    df['60_80'] = 0
    df['Over80'] = 0

    df.loc[df['EtaDecesso'] < 20, '0_20'] = 1
    df.loc[(df['EtaDecesso'] >= 20) & (df['EtaDecesso'] < 40), '20_40'] = 1
    df.loc[(df['EtaDecesso'] >= 40) & (df['EtaDecesso'] < 60), '40_60'] = 1
    df.loc[(df['EtaDecesso'] >= 60) & (df['EtaDecesso'] < 80), '60_80'] = 1
    df.loc[(df['EtaDecesso'] >= 80), 'Over80'] = 1

    # Chart
    #output_file(outf, title="Decessi")

    fasce = df[['0_20','20_40','40_60','60_80','Over80']].resample('AS').sum()
    source = ColumnDataSource(fasce)
    #colors = small_palettes['Viridis'][5]
    colors = void.palette5
    labels = ('Under 20','20-40','40-60','60-80','Over 80')

    p = figure(plot_width=800, plot_height=400, x_axis_type="datetime",
            title="DECESSI")


    v = p.vbar_stack(['0_20','20_40','40_60','60_80','Over80'], x='DataDecesso',
                width=timedelta(days=180),
                color=colors,
                source=source)

    p.add_tools(HoverTool(tooltips=[
        (labels[4], "@Over80"),
        (labels[3], "@40_60"),
        (labels[2], "@60_80"),
        (labels[1], "@20_40"),
        (labels[0], "@0_20"),
    ]))

    legend = Legend(items=[
        (labels[4],   [v[4]]),
        (labels[3],   [v[3]]),
        (labels[2],   [v[2]]),
        (labels[1],   [v[1]]),
        (labels[0],   [v[0]]),
    ], location=(0, 0))

    p.add_layout(legend, 'right')


    # Details
    #cols = [p]
    #for i,top in enumerate(['0_20','20_40','40_60','60_80','Over80']):
    #    b = figure(plot_width=800, plot_height=400, x_axis_type="datetime",
    #               title=top)
    #    b.vbar(top=top, x='DataDecesso',
    #                width=timedelta(days=180),
    #                color=colors[i],
    #                source=source)
    #    cols.append(b)
    #
    #save(column(cols))
    #save(p)

    p.xaxis.axis_label = 'Anno'
    p.yaxis.axis_label = 'Decessi'

    void.setup_fonts(p)

    return p

