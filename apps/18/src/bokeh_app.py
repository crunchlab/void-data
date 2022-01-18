"""
VOID App 18 - Decessi San Stino di Livenza

Veneto Orientale Innovation District

January 2022

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

def convert_dataset(df):
    """
    Create a new dataset from the input one with columns
    sesso,data nascita,data decesso,eta decesso

    to

    FasciaEta;Maschi;Femmine;Totale

    Parameters
    ==========
    df: DataFrame

    Returns
    =======
    DataFrame
    """

    # remove unused columns
    df = df.drop(columns=['data nascita', 'data decesso'])

    # get the mask for males
    maschi = df['sesso'] == 'M'

    # set the counters
    df['t'] = 1  # totals
    df['m'] = 0  # males
    df['f'] = 0  # females

    # set the males using the mask
    df.loc[maschi, 'm'] = 1

    # set the female as the not males
    df.loc[~maschi, 'f'] = 1

    # 'sesso' column now is not yet necessary
    df = df.drop(columns=['sesso'])

    # one row per age
    grp = df.groupby(by=['eta decesso']).sum()

    # new dataframe from the groupby
    return pd.DataFrame({'FasciaEta': grp.index,
                         'Maschi': grp['m'],
                         'Femmine': grp['f'],
                         'Totale': grp['t']})


def build_layout(df):

    source = ColumnDataSource(df)
    colors = (void.color_table['blue'], void.color_table['red'])
    labels = ('Maschi','Femmine')

    p = figure(plot_width=800, plot_height=400, title="Decessi per Età")

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
    p.yaxis.axis_label = 'Decessi'

    void.setup_fonts(p)

    return p


def main(datafile, htmlout):
    # read the data and convert the dataframe
    dd = pd.read_csv(datafile)
    df = convert_dataset(dd)
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
