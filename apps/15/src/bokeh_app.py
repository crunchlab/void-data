"""
VOID App 15 - Migrazioni Concordia Sagittaria

Veneto Orientale Innovation District

December 2021

"""

print("Loading libraries...")

from math import pi

import pandas as pd

#from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.models import ColumnDataSource

import void

def build_balance(df):
    """
    Parameters
    ===========
    df: dataframe
    """

    age_range = df.index.values

    p = figure(height=400, title="Bilancio Migratorio")

    p.vbar(x=age_range, top=df['bilancio'], width=6,
           color=void.color_table['black'])

    p.add_tools(HoverTool(
                   tooltips=[('FASCIA ETA',"@x"),
                             ("MIGRANTI","@top")]))

    p.xaxis.axis_label = 'Fascia Età'
    p.yaxis.axis_label = "Migranti"

    p.legend.location = "bottom_right"

    void.setup_fonts(p)

    return p

def build_details(df):
    """
    Parameters
    ===========
    df: dataframe
    """
    hdf = df
    hdf['Nemigrati femmine'] = df['emigrati femmine'] * -1
    hdf['Nemigrati maschi'] = df['emigrati maschi'] * -1

    source = ColumnDataSource(hdf)
    colors = [void.color_table['red'], void.color_table['blue'],
              void.color_table['pink'], void.color_table['light_blue']]
    labels=['im. femmine','im. maschi','em. femmine', 'em. maschi']

    y_range = (-100,100)
    width=6

    p = figure(y_range=y_range, height=600, title="Dettaglio Migrazioni")

    p.vbar_stack(['immigrati femmine','immigrati maschi'], x='FasciaEta',
                width=width, color=colors[:2], source=source,
                legend_label=labels[:2])

    p.vbar_stack(['Nemigrati femmine','Nemigrati maschi'], x='FasciaEta',
                width=width, color=colors[2:], source=source,
                legend_label=labels[2:])

    p.add_tools(HoverTool(
                   tooltips=[('FASCIA ETA',"@FasciaEta"),
                             ("Im. Femmine","@{immigrati femmine}"),
                             ("Im. Maschi","@{immigrati maschi}"),
                             ("Em. Femmine","@{emigrati femmine}"),
                             ("Em. Maschi","@{emigrati maschi}"),
                             ]))

    p.xaxis.axis_label = 'Fascia Età'
    p.yaxis.axis_label = "Migranti"

    p.legend.location = "bottom_right"

    void.setup_fonts(p)

    return p

def main(datafile, htmlout):
    # read the data and prepare the dataframe
    df = pd.read_csv(datafile)
    df = df.drop(['deceduti maschi', 'deceduti femmine'], axis=1)
    df.set_index('Anno Nascita', inplace=True)
    df['FasciaEta'] = ((2020 - df.index) // 10) * 10

    gdf = df.groupby('FasciaEta').sum()
    gdf['emigrati'] = gdf['emigrati maschi'] + gdf['emigrati femmine']
    gdf['immigrati'] = gdf['immigrati maschi'] + gdf['immigrati femmine']
    gdf['bilancio'] = gdf['immigrati'] - gdf['emigrati']

    # composite the HTML
    layout_details = build_details(gdf)
    layout_balance = build_balance(gdf)

#    from bokeh.io import export_png
#    export_png(layout_balance, filename="bilancio.png", width=800, height=600)
#    export_png(layout_details, filename="dettaglio.png", width=800, height=600)

    with open('template.html', 'r') as ftempl:
        htmltempl = ftempl.read()

        script, div = components(layout_details)
        htmltempl = htmltempl.replace('$BOKEH_DIV_DET$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_DET$', script)

        script, div = components(layout_balance)
        htmltempl = htmltempl.replace('$BOKEH_DIV_BAL$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_BAL$', script)

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

#    datafile = 'data/movimenti_migratori.csv'
#    htmlout = 'index.html'

    main(datafile, htmlout)
