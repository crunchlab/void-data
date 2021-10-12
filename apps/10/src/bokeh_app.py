from datetime import datetime
import pandas as pd
import void

from bokeh.io import export_png

from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource
from bokeh.palettes import small_palettes
from bokeh.models import Legend
from bokeh.layouts import row, column
from bokeh.models import HoverTool
from bokeh.embed import components

def build_vbar(df, title, color):
    """
    Create the Vertical Bar layout

    Parameters
    ===========
    df: DataFrame
    title: str
    """
    bins = df.groupby('ETA').count()

    source = ColumnDataSource(dict(x=bins.index, top=bins['SESSO']))

    p = figure(plot_width=800, plot_height=400, title=title)
    v = p.vbar(source=source, x='x', top='top', bottom=0,
               fill_alpha=0.8, line_color='black', fill_color=color)
    p.add_tools(HoverTool(tooltips=[('ETA',"@x"),('DECESSI',"@top")]))

    p.xaxis.axis_label = 'Età'
    p.yaxis.axis_label = 'Decessi'

    void.setup_fonts(p)

    return p

def build_lines(dfm, dff, title):
    """
    Create the two lines plot

    Parameters
    ===========
    dfm: Male DataFrame
    dff: Female DataFrame
    title: str
    """

    sourcef = ColumnDataSource(dict(x=dff.index, y=dff['ETA']))
    sourcem = ColumnDataSource(dict(x=dfm.index, y=dfm['ETA']))

    p = figure(x_axis_type="datetime", plot_width=800, plot_height=400, title=title)

    p.line(source=sourcef, line_color='red', line_width=3, legend_label='FEMMINE')
    p.line(source=sourcem, line_color='blue', line_width=3, legend_label='MASCHI')

    p.add_tools(HoverTool(
                   formatters={"@x": "datetime"},
                   tooltips=[('ANNO',"@x{%F}"),('DECESSI',"@y")]))

    p.xaxis.axis_label = 'Anno'
    p.yaxis.axis_label = 'Decessi'

    p.legend.location = "bottom_right"

    void.setup_fonts(p)

    return p

def main(datafile, htmlout):

    # read the data and prepare the dataframe
    date_parser = lambda x: datetime.strptime(x, "%d/%m/%y")

    df = pd.read_csv(datafile, sep=';', parse_dates=['DATA DECESSO'],
                     date_parser=date_parser)
    df.drop("DATA NASCITA", axis=1, inplace=True)

    maschi_mask = df["SESSO"] == 'M'
    femmine_mask = df["SESSO"] == 'F'

    maschi = df[maschi_mask]
    femmine = df[femmine_mask]

    vbarm = build_vbar(maschi,
                      "DECESSI SULLA POPOLAZIONE MASCHILE",
                      void.color_table["blue"])
    vbarf = build_vbar(femmine,
                      "DECESSI SULLA POPOLAZIONE FEMMINILE",
                      void.color_table["red"])

#    export_png(vbarm, filename="maschi.png", width=1600, height=1000)
#    export_png(vbarf, filename="femmine.png", width=1600, height=1000)

    # Aggregation by Year
    m = maschi.set_index(maschi['DATA DECESSO'])
    m = m.resample('A').count()

    f = femmine.set_index(femmine['DATA DECESSO'])
    f = f.resample('A').count()

    lines = build_lines(m, f, "DECESSI DAL 2000 AL 2020")

    export_png(lines, filename="lines.png", width=1600, height=1000)

#    # to html

    with open('template.html', 'r') as ftempl:
        htmltempl = ftempl.read()

        script, div = components(vbarm)
        htmltempl = htmltempl.replace('$BOKEH_DIV_MASCHI$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_MASCHI$', script)

        script, div = components(vbarf)
        htmltempl = htmltempl.replace('$BOKEH_DIV_FEMMINE$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_FEMMINE$', script)

        script, div = components(lines)
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

#    datafile = 'data/decessi_jesolo.csv'
#    htmlout = 'index.html'

    main(datafile, htmlout)
