"""
VOID App 12 - Decessi Portogruaro

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

from datetime import timedelta
import void

c_sesso = "Sesso"
c_dt_nascita = "DataNascita"
c_dt_decesso = "DataMorte"
c_eta = "Eta"

def build_lines(df):
    """
    Lines Plot for mean of age for each year.
    3 lines: male, female, all
    """

    title = "Variazione Età Media Decesso nel Tempo"

    male_mask = df['Sesso'] == 'M'

    # all
    dfa = df.resample('Y')['Eta'].mean()

    # male
    dfm = df[male_mask].resample('Y')['Eta'].mean()

    # female (only male and female in the dataset)
    dff = df[~male_mask].resample('Y')['Eta'].mean()

    sourcea = ColumnDataSource(dict(x=dfa.index, y=dfa.values))
    sourcem = ColumnDataSource(dict(x=dfm.index, y=dfm.values))
    sourcef = ColumnDataSource(dict(x=dff.index, y=dff.values))

    p = figure(x_axis_type="datetime", plot_width=800, plot_height=400, title=title)

    p.line(source=sourcea, line_color='black', line_width=3, legend_label='TUTTI')
    p.line(source=sourcef, line_color='red', line_width=3, legend_label='FEMMINE')
    p.line(source=sourcem, line_color='blue', line_width=3, legend_label='MASCHI')

    p.add_tools(HoverTool(
                   formatters={"@x": "datetime"},
                   tooltips=[('ANNO',"@x{%F}"),("ETA'","@y")]))

    p.xaxis.axis_label = 'Anno'
    p.yaxis.axis_label = "Età Media"

    p.legend.location = "bottom_right"

    void.setup_fonts(p)

#    from bokeh.io import export_png
#    export_png(p, filename="lines.png", width=1600, height=1200)

    return p

def build_fasce(df):
    """
    Stacked bar for each age rage per year
    """
    # Fasce d'Eta'
    df['0_20'] = 0
    df['20_40'] = 0
    df['40_60'] = 0
    df['60_80'] = 0
    df['Over80'] = 0

    df.loc[df[c_eta] < 20, '0_20'] = 1
    df.loc[(df[c_eta] >= 20) & (df[c_eta] < 40), '20_40'] = 1
    df.loc[(df[c_eta] >= 40) & (df[c_eta] < 60), '40_60'] = 1
    df.loc[(df[c_eta] >= 60) & (df[c_eta] < 80), '60_80'] = 1
    df.loc[(df[c_eta] >= 80), 'Over80'] = 1

    # Chart

    fasce = df[['0_20','20_40','40_60','60_80','Over80']].resample('AS').sum()

    source = ColumnDataSource(fasce)
    colors = void.palette5
    labels = ('Under 20','20-40','40-60','60-80','Over 80')

    p = figure(plot_width=800, plot_height=400, x_axis_type="datetime",
            title="DECESSI")


    v = p.vbar_stack(['0_20','20_40','40_60','60_80','Over80'], x=c_dt_decesso,
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

    p.xaxis.axis_label = 'Anno'
    p.yaxis.axis_label = 'Decessi'

    void.setup_fonts(p)

#    from bokeh.io import export_png
#    export_png(p, filename="fasce.png", width=1600, height=1200)

    return p

# end build_fasce


def main(datafile, htmlout):
    # read the data and prepare the dataframe
    df = pd.read_csv(datafile, sep=';')
    df['DataNascita'] = pd.to_datetime(df['DataNascita'], format='%d/%m/%Y')
    df['DataMorte'] = pd.to_datetime(df['DataMorte'], format='%d/%m/%Y')

    # remove partial data
    df.set_index('DataMorte', inplace=True)
    df.drop(df.loc['1999'].index, inplace=True)

    # build the HTML
    layout_lines = build_lines(df)
    layout_fasce = build_fasce(df)

    with open('template.html', 'r') as ftempl:
        htmltempl = ftempl.read()

        script, div = components(layout_fasce)
        htmltempl = htmltempl.replace('$BOKEH_DIV_FASCE$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_FASCE$', script)

        script, div = components(layout_lines)
        htmltempl = htmltempl.replace('$BOKEH_DIV_LINES$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_LINES$', script)

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

#    datafile = '../data/mortalitaPortogruaro.csv'
#    htmlout = 'index.html'

    main(datafile, htmlout)
