"""
VOID App 08 - Distribuzione Popolazione Nata a Noventa di Piave

Veneto Orientale Innovation District

September 2021

The dataset has a row for each person born in the Comune
"""

print("Loading libraries...")

from math import pi

import pandas as pd

from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.palettes import Set3
from bokeh.embed import components

import void

# FIXME argparse

def ita_vs_foreigns(df):
    """
    Get a Series from the entire DataFrame
    counting Italians and Foreigners

    Parameters
    ===========
    df: DataFrame

    Returns
    ========
    s: Series, index=['Italiani', 'Stranieri']
    """
    # Masks
    italiano = df['Cittadinanza'] == 'ITALIANA'

    # to series
    ita = italiano.value_counts()
    vals = {'Italiani': ita[True],
            'Stranieri': ita[False]}
    return pd.Series(data=vals, index=['Italiani','Stranieri'])

def ita_details(df):
    """
    Get a Series from the entire DataFrame
    extracting the italians and grouping by the ProviciaNascita

    Parameters
    ===========
    df: DataFrame

    Returns
    ========
    s: Series, index=ProvinciaNascita, value=count
    """
    # Masks
    italiano = df['Cittadinanza'] == 'ITALIANA'

    # to series
    return df[italiano]['ProvinciaNascita'].value_counts()

def foreigns_details(df):
    """
    Get a Series from the entire DataFrame
    extracting the not italians and grouping by the Cittadinanza

    Parameters
    ===========
    df: DataFrame

    Returns
    ========
    s: Series, index=Cittadinanza, value=count
    """
    # Masks
    italiano = df['Cittadinanza'] == 'ITALIANA'

    # to series
    return df[~italiano]['Cittadinanza'].value_counts()


def build_layout_pie(series, title, thr=0, colorf=None):
    """
    Build the Bokeh Figure for the series

    Parameters
    ==========
    series: pd.Series
    title: str
    thr: int, [opz]
    colorf: function to map str to color

    Returns
    =========
    figure
    """
    data = pd.DataFrame({'label': series.index, 'amount': series.values})

    if thr > 0:
        # compress data below the threshold
        mask_thr = data['amount'] < thr
        others = data[mask_thr]['amount'].sum()
        data = data.drop(data[mask_thr].index)
        data = data.append({'label': 'ALTRI', 'amount': others}, ignore_index=True)

    data['angle'] = data['amount']/data['amount'].sum() * 2*pi

    if colorf:
        data['color'] = colorf(data['label'].values)
    else:
        data['color'] = Set3[12][:len(data)]

    p = figure(plot_height=350, title=title, x_range=(-0.5, 1.0),
               toolbar_location=None, tools="hover", tooltips="@label: @amount" )

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='label', source=data)

    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None

    void.setup_fonts(p)

    return p

def color_prov(provs):
    """
    Convert an array of Provincia in colors, with consistency
    Retuns
    ========
    colors: [color]
    """
    palette = Set3[12]

    prov_colors = {}

    for i, p in enumerate([ 'VE', 'TV', 'PD', 'UD', 'ALTRI']):
        prov_colors[p] = palette[i]

    return [prov_colors.get(p, palette[-1]) for p in provs]

def color_states(states):
    """
    Convert an array of State in colors, with consistency
    Retuns
    ========
    colors: [color]
    """
    known_states = [
        'ALBANESE',
        'BENGALESE',
        'BOSNIACA',
        'CINESE',
        'GHANESE',
        'JUGOSLAVA',
        'KOSOVARA',
        'MAROCCHINA',
        'MOLDAVA',
        'NIGERIANA',
        'RUMENA',
        'SENEGALESE',
    ]

    palette = Set3[12]

    state_colors = {}

    for i,s in enumerate(known_states):
        state_colors[s] = palette[i]

    return [state_colors.get(s, '#f9f9f9') for s in states]


def main(datafile, htmlout):
    # read the data and prepare the dataframe
    df = pd.read_csv(datafile, sep=',', keep_default_na=False)
    df['DataNascita'] = pd.to_datetime(df['DataNascita'], format='%Y-%m-%d')
    df.set_index('DataNascita', inplace=True)


    # 2 decades
    df2010 = df.loc['2001-01-01':'2010-01-01']
    df2020 = df.loc['2010-01-01':'2020-01-01']

    # 2010
    s_ita_vs_foreigns = ita_vs_foreigns(df2010)
    s_ita_details = ita_details(df2010)
    s_foreigns_details = foreigns_details(df2010)

    # to chart
    layout2010_all = build_layout_pie(s_ita_vs_foreigns, 'Rapporto Italiani e Stranieri (2000-2010)')

    layout2010_ita = build_layout_pie(s_ita_details,
                    'Dettaglio Italiani (2000-2010)',
                    thr=4, colorf=color_prov)

    layout2010_for = build_layout_pie(s_foreigns_details,
                     'Dettaglio Stranieri (2000-2010)',
                     thr=4, colorf=color_states)

    # 2020
    s_ita_vs_foreigns = ita_vs_foreigns(df2020)
    s_ita_details = ita_details(df2020)
    s_foreigns_details = foreigns_details(df2020)

    # to chart
    layout2020_all = build_layout_pie(s_ita_vs_foreigns, 'Rapporto Italiani e Stranieri (2010-2020)')

    layout2020_ita = build_layout_pie(s_ita_details,
                     'Dettaglio Italiani (2010-2020)',
                     thr=4, colorf=color_prov)

    layout2020_for = build_layout_pie(s_foreigns_details,
                     'Dettaglio Stranieri (2010-2020)',
                     thr=5, colorf=color_states)

    # composite the HTML

    with open('template.html', 'r') as ftempl:
        htmltempl = ftempl.read()

        # 2010
        script, div = components(layout2010_all)
        htmltempl = htmltempl.replace('$BOKEH_DIV_2010_ALL$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_2010_ALL$', script)

        script, div = components(layout2010_ita)
        htmltempl = htmltempl.replace('$BOKEH_DIV_2010_ITA$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_2010_ITA$', script)

        script, div = components(layout2010_for)
        htmltempl = htmltempl.replace('$BOKEH_DIV_2010_FOR$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_2010_FOR$', script)

        # 2020
        script, div = components(layout2020_all)
        htmltempl = htmltempl.replace('$BOKEH_DIV_2020_ALL$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_2020_ALL$', script)

        script, div = components(layout2020_ita)
        htmltempl = htmltempl.replace('$BOKEH_DIV_2020_ITA$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_2020_ITA$', script)

        script, div = components(layout2020_for)
        htmltempl = htmltempl.replace('$BOKEH_DIV_2020_FOR$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_2020_FOR$', script)

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

#    datafile = 'data/APR_Noventa_20210409.csv'
#    htmlout = 'index.html'

    main(datafile, htmlout)
