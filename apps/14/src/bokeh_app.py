"""
VOID App 14 - Demografia Concordia Sagittaria

Veneto Orientale Innovation District

November 2021

"""

print("Loading libraries...")

from math import pi

import pandas as pd

from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.palettes import Set3
from bokeh.layouts import row, column
from bokeh.embed import components
from bokeh.models import CheckboxGroup, Button
from bokeh.models.callbacks import CustomJS
from bokeh.models import HoverTool

import void

def build_lines_weddings_a(df):
    """
    Create the lines plot for weddings data, absolute data

    Parameters
    ===========
    df: dataframe
    """

    labels = ['MATRIMONI','DIVORZI','FAMIGLIE (migliaia)']

    p = figure(plot_width=800, plot_height=400,
               title="Matrimoni e Divorzi Assoluti")

    w = p.line(df.index, df['matrimoni'],
               name='matrimoni',
               line_color=void.color_table['green'], line_width=3,
               legend_label=labels[0])

    d = p.line(df.index, df['divorzi'],
               name='divorzi',
               line_color=void.color_table['red'], line_width=3,
               legend_label=labels[1])

    f = p.line(df.index, df['famiglie_k'],
               name='famiglie',
               line_color=void.color_table['gray'], line_width=3,
               line_dash='dashed',
               legend_label=labels[2])

    p.add_tools(HoverTool(
                   renderers=[w],
                   tooltips=[('ANNO',"@x"), (labels[0],"@y")]))
    p.add_tools(HoverTool(
                   renderers=[d],
                   tooltips=[('ANNO',"@x"), (labels[1],"@y")]))
    p.add_tools(HoverTool(
                   renderers=[f],
                   tooltips=[('ANNO',"@x"), (labels[2],"@y")]))

    p.xaxis.axis_label = 'Anno'
    p.yaxis.axis_label = 'Totale'

#    p.legend.location = "bottom_right"

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
    checkbox_group = CheckboxGroup(labels=labels, active=[0, 1, 2])
    checkbox_group.js_on_click(checkbox_cb)

    layout = column(p, checkbox_group)

    return layout

def build_lines_weddings_r(df):
    """
    Create the lines plot for weddings data, relative data

    Parameters
    ===========
    df: dataframe
    """

    labels = ['MATRIMONI','DIVORZI']

    p = figure(plot_width=800, plot_height=400,
               title="Matrimoni e Divorzi Relativi")

    w = p.line(df.index, df['matrimoni_perc'],
               name='matrimoni',
               line_color=void.color_table['green'], line_width=3,
               legend_label=labels[0])

    d = p.line(df.index, df['divorzi_perc'],
               name='divorzi',
               line_color=void.color_table['red'], line_width=3,
               legend_label=labels[1])

    p.add_tools(HoverTool(
                   renderers=[w],
                   tooltips=[('ANNO',"@x"), (labels[0],"@y %")]))
    p.add_tools(HoverTool(
                   renderers=[d],
                   tooltips=[('ANNO',"@x"), (labels[1],"@y %")]))

    p.xaxis.axis_label = 'Anno'
    p.yaxis.axis_label = 'Percentuale su Famiglie'

#    p.legend.location = "bottom_right"

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
    checkbox_group = CheckboxGroup(labels=labels, active=[0, 1])
    checkbox_group.js_on_click(checkbox_cb)

    layout = column(p, checkbox_group)

    return layout

def build_lines_migrants_a(df):
    """
    Create the lines plot for migrants data, absolute data

    Parameters
    ===========
    df: dataframe
    """

    labels = ['IMMIGRATI','EMIGRATI','POPOLAZIONE (migliaia)']

    p = figure(plot_width=800, plot_height=400,
               title="Migrazioni Assolute")

    w = p.line(df.index, df['immigrati'],
               name='immigrati',
               line_color=void.color_table['green'], line_width=3,
               legend_label=labels[0])

    d = p.line(df.index, df['emigrati'],
               name='emigrati',
               line_color=void.color_table['red'], line_width=3,
               legend_label=labels[1])

    f = p.line(df.index, df['popolazione_k'],
               name='popolazione',
               line_color=void.color_table['gray'], line_width=3,
               line_dash='dashed',
               legend_label=labels[2])

    p.add_tools(HoverTool(
                   renderers=[w],
                   tooltips=[('ANNO',"@x"), (labels[0],"@y")]))
    p.add_tools(HoverTool(
                   renderers=[d],
                   tooltips=[('ANNO',"@x"), (labels[1],"@y")]))
    p.add_tools(HoverTool(
                   renderers=[f],
                   tooltips=[('ANNO',"@x"), (labels[2],"@y")]))

    p.xaxis.axis_label = 'Anno'
    p.yaxis.axis_label = 'Totale'

    p.legend.location = "center_right"

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
    checkbox_group = CheckboxGroup(labels=labels, active=[0, 1, 2])
    checkbox_group.js_on_click(checkbox_cb)

    layout = column(p, checkbox_group)

    return layout

def build_lines_migrants_r(df):
    """
    Create the lines plot for migrants data, reletive data

    Parameters
    ===========
    df: dataframe
    """

    labels = ['IMMIGRATI','EMIGRATI']

    p = figure(plot_width=800, plot_height=400,
               title="Migrazioni Relative")

    w = p.line(df.index, df['immigrati_perc'],
               name='immigrati',
               line_color=void.color_table['green'], line_width=3,
               legend_label=labels[0])

    d = p.line(df.index, df['emigrati_perc'],
               name='emigrati',
               line_color=void.color_table['red'], line_width=3,
               legend_label=labels[1])

    p.add_tools(HoverTool(
                   renderers=[w],
                   tooltips=[('ANNO',"@x"), (labels[0],"@y %")]))
    p.add_tools(HoverTool(
                   renderers=[d],
                   tooltips=[('ANNO',"@x"), (labels[1],"@y %")]))

    p.xaxis.axis_label = 'Anno'
    p.yaxis.axis_label = 'Percentuale su Popolazione'

    p.legend.location = "bottom_right"

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
    checkbox_group = CheckboxGroup(labels=labels, active=[0, 1, 2])
    checkbox_group.js_on_click(checkbox_cb)

    layout = column(p, checkbox_group)

    return layout

def main(datafile, htmlout):
    # read the data and prepare the dataframe
    df = pd.read_csv(datafile, sep=';')
    df.set_index('anno', inplace=True)

    # add rations
    df['famiglie_k'] = df['famiglie'] / 1000
    df['popolazione_k'] = df['popolazione'] / 1000
    df['immigrati_perc'] = (100*df['immigrati']/df['popolazione']).round(1)
    df['emigrati_perc'] = (100*df['emigrati']/df['popolazione']).round(1)
    df['divorzi_perc'] = (100*df['divorzi']/df['famiglie']).round(1)
    df['matrimoni_perc'] = (100*df['matrimoni']/df['famiglie']).round(1)

    # composite the HTML
    layout_wed_a = build_lines_weddings_a(df)
    layout_wed_r = build_lines_weddings_r(df)
    layout_mig_a = build_lines_migrants_a(df)
    layout_mig_r = build_lines_migrants_r(df)

    with open('template.html', 'r') as ftempl:
        htmltempl = ftempl.read()

        script, div = components(layout_wed_a)
        htmltempl = htmltempl.replace('$BOKEH_DIV_WED_A$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_WED_A$', script)

        script, div = components(layout_wed_r)
        htmltempl = htmltempl.replace('$BOKEH_DIV_WED_R$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_WED_R$', script)

        script, div = components(layout_mig_a)
        htmltempl = htmltempl.replace('$BOKEH_DIV_MIG_A$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_MIG_A$', script)

        script, div = components(layout_mig_r)
        htmltempl = htmltempl.replace('$BOKEH_DIV_MIG_R$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_MIG_R$', script)

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

#    datafile = 'data/anagrafe.csv'
#    htmlout = 'index.html'

    main(datafile, htmlout)
