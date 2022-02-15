"""
VOID App 20 - Migrazioni 6 Comuni VOID

Veneto Orientale Innovation District

February 2022

"""

print("Loading libraries...")

import pandas as pd
import numpy as np
from math import pi

from bokeh.models import LogTicker, ColorBar, PrintfTickFormatter
from bokeh.models import LogColorMapper
from bokeh.plotting import figure
from bokeh.palettes import RdYlGn
from bokeh.embed import components

import void

def build_layout(df):
    """
    Create the Heatmap
    """
    title = "Migrazioni tra Comuni VOID (2000-2020)"

    x = sorted(list(df['start'].value_counts().index))
    y = x

    colors = RdYlGn[6]
    # Use log scale because the data are in a big range
    mapper = LogColorMapper(palette=colors, low_color='darkgray',
                            low=1, high=df['weight'].max())

    p = figure(title=title, x_range=x, y_range=y,
               width=800, height=600,tools="save,hover",
               tooltips=[('DA', '@start'),
                         ('A', '@end'),
                         ('PERSONE', '@weight')])

    p.rect(x="end", y="start", width=1, height=1,
           source=df,
           fill_color={'field': 'weight', 'transform': mapper},
           line_color='black')

    # rotate the X labels
    p.xaxis.major_label_orientation = pi / 3

    # The legend is the colorbar
    color_bar = ColorBar(color_mapper=mapper,
                        ticker=LogTicker(desired_num_ticks=len(colors)),
                        formatter=PrintfTickFormatter(format="%d"),
                        label_standoff=6, border_line_color=None)

    p.add_layout(color_bar, 'right')

    void.setup_fonts(p)

    return p


def load_datasets(datadir):
    """
    Load an aggregation of all the datasets in the datadir.
    It loads
    - jesolo.csv
    - musile.csv
    - portogruaro.csv
    - sandona.csv
    - sanstino.csv
    - noventa.csv

    Valid only from '2000-01-03' to '2020-12-18'.

    Parameters
    ===========
    datadir: str, the location for the 'data' directory

    Returns
    =========
    df: DataFrame['start','end',weight'] sorted ['start','end']
    """

    import os

    # Jesolo
    df_js = pd.read_csv(os.path.join(datadir,'jesolo.csv'))
    df_js['data'] = pd.to_datetime(df_js['DATA_ISCRIZIONE'],format='%d/%m/%y')
    df_js['end'] = 'JESOLO'
    df_js['start'] = df_js['COMUNE_PROVENIENZA']
    df_js = df_js.dropna()
    df_js.drop(columns=['COMUNE_PROVENIENZA','STATO_PROVENIENZA',
                        'DATA_ISCRIZIONE','PROVINCIA_PROVENIENZA'],
                        inplace=True)

    # Musile di Piave
    df_mu = pd.read_csv(os.path.join(datadir,'musile.csv'))
    df_mu['data'] = pd.to_datetime(df_mu['DATA'],format='%Y-%m-%d')
    df_mu['end'] = 'MUSILE DI PIAVE'
    df_mu['start'] = df_mu['COMUNE PROVENIENZA']
    df_mu = df_mu.dropna()
    df_mu.drop(columns=['COMUNE PROVENIENZA','STATO PROVENIENZA',
                        'DATA','PR PROVENIENZA'], inplace=True)

    # Portogruaro
    df_po = pd.read_csv(os.path.join(datadir,'portogruaro.csv'))
    df_po['data'] = pd.to_datetime(df_po['DataImmigrazione'],format='%d/%m/%Y')
    df_po['end'] = 'PORTOGRUARO'
    df_po['start'] = df_po['LuogoProvenienza'].str.strip()
    df_po = df_po.dropna()
    df_po.drop(columns=['Sesso','DataImmigrazione','LuogoProvenienza',
                        'Provincia','Stato'], inplace=True)

    # San Donà di Piave
    df_sd = pd.read_csv(os.path.join(datadir,'sandona.csv'))
    df_sd['data'] = pd.to_datetime(df_sd['DATA'],format='%Y-%m-%d')
    df_sd['end'] = 'SAN DONÀ DI PIAVE'
    df_sd['start'] = df_sd['COMUNE PROVENIENZA']
    df_sd= df_sd.dropna()
    df_sd.drop(columns=['DATA','COMUNE PROVENIENZA',
                        'STATO PROVENIENZA','PR PROVENIENZA'], inplace=True)

    # San Stino di Livenza
    df_ss = pd.read_csv(os.path.join(datadir,'sanstino.csv'))
    df_ss['data'] = pd.to_datetime(df_ss['DATA IMMIGRAZIONE'],format='%d-%m-%Y')
    df_ss['end'] = 'SAN STINO DI LIVENZA'
    df_ss['start'] = df_ss['COMUNE DI PROVENIENZA']
    df_ss= df_ss.dropna()
    df_ss.drop(columns=['DATA IMMIGRAZIONE','SESSO','COMUNE DI PROVENIENZA',
                        'STATO DI PROVENIENZA','PROVINCIA DI PROVENIENZA'],
                        inplace=True)

    # Noventa di Piave
    df_no = pd.read_csv(os.path.join(datadir,'noventa.csv'))
    df_no['data'] = pd.to_datetime(df_no['DATA IMMIGRAZIONE'],format='%Y-%m-%d')
    df_no['end'] = 'NOVENTA DI PIAVE'
    df_no['start'] = df_no['COMUNE PROVENIENZA']
    df_no= df_no.dropna()
    df_no.drop(columns=['DATA IMMIGRAZIONE','COMUNE PROVENIENZA',
                        'STATO PROVENIENZA','PR PROVENIENZA'], inplace=True)

    # Merge
    df = pd.concat([df_no,df_sd,df_js,df_mu,df_po,df_ss])

    # Solo i comuni VOID
    ar = ['NOVENTA DI PIAVE','SAN DONÀ DI PIAVE','PORTOGRUARO','SAN STINO DI LIVENZA','MUSILE DI PIAVE','JESOLO']
    # Maschera
    ms = df['start'].isin(ar)
    me = df['end'].isin(ar)
    dd = df[ms & me].set_index('data')

    # restrizione su date comuni a tutti i dataset
    dd = dd.loc['2000-01-03':'2020-12-18']

    # Creazione aggregazione per network

    dd['weight'] = 1
    de = dd.groupby(['start','end']).sum().reset_index()
    de = de.sort_values(by=['start','end'])

    # Rimuove i flussi intracomune
    mask_eq = de['start'] == de['end']
    de.loc[mask_eq,'weight'] = 0

    return de


def main(datadir, htmlout):

    df = load_datasets(datadir)


    # build the HTML

    layout = build_layout(df)

    with open('template.html', 'r') as ftempl:
        htmltempl = ftempl.read()

        script, div = components(layout)
        htmltempl = htmltempl.replace("$BOKEH_DIV$", div)
        htmltempl = htmltempl.replace("$BOKEH_SCRIPT$", script)

        with open(htmlout, 'w') as fout:
            fout.write(htmltempl)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('datadir', type=str)
    parser.add_argument('htmlfile', type=str)

    args = parser.parse_args()

    datadir = args.datadir
    htmlout = args.htmlfile

    main(datadir, htmlout)
