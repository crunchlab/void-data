"""
VOID App 13 - Statistiche Concordia Sagittaria

Veneto Orientale Innovation District

November 2021

"""

print("Loading libraries...")

from math import pi

import pandas as pd

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.models import Legend

import void

def build_layout(df):

    source = ColumnDataSource(df)
    colors = (void.color_table['blue'], void.color_table['red'])
    labels = ('Maschi','Femmine')

    p = figure(plot_width=800, plot_height=400, title="Residenti per Età")

    v = p.vbar_stack(['Maschi','Femmine'], x="FasciaEta",
                color=colors,
                source=source)

    p.add_tools(HoverTool(tooltips=[
        ("Età",     "@FasciaEta"),
        (labels[1], "@Femmine"),
        (labels[0], "@Maschi"),
    ]))

    legend = Legend(items=[
        (labels[1],   [v[1]]),
        (labels[0],   [v[0]]),
    ], location=(0, 0))

    p.add_layout(legend, 'right')

    p.xaxis.axis_label = 'Età'
    p.yaxis.axis_label = 'Residenti'

    void.setup_fonts(p)

    return p


def main(datafile, htmlout):
    # read the data and prepare the dataframe
    df = pd.read_csv(datafile, sep=';')
    df.set_index('FasciaEta', inplace=True)


    # build the HTML
    layout = build_layout(df)

    with open('template.html', 'r') as ftempl:
        htmltempl = ftempl.read()

        script, div = components(layout)
        htmltempl = htmltempl.replace('$BOKEH_DIV$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT$', script)

        with open(htmlout, 'w') as fout:
            fout.write(htmltempl)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('datafile', type=str)
    parser.add_argument('htmlfile', type=str)

    args = parser.parse_args()

    datafile = args.datafile
    htmlout = args.htmlfile

#    datafile = 'data/residenti_fascia_eta.csv'
#    htmlout = 'index.html'

    main(datafile, htmlout)
