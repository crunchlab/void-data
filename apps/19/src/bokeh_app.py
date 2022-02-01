"""
VOID App 19 - Decessi 6 Comuni

Veneto Orientale Innovation District

January 2022

"""

print("Loading libraries...")

import pandas as pd
import numpy as np

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.models import Legend
from bokeh.transform import dodge

import void

NAMES = [('SD','San Donà di Piave'),
         ('JS','Jesolo'),
         ('MU','Musile di Piave'),
         ('NO','Noventa di Piave'),
         ('SS','San Stino di Livenza'),
         ('PO','Portogruaro'),
        ]

GENDER = {'T': 'Decessi', 'M': 'Decessi Maschi', 'F': 'Decessi Femmine'}
MESI = ['Gen.', 'Feb.', 'Mar.','Apr.','Mag.','Giu.','Lug.','Ago.','Set.','Ott.','Nov.','Dic.']

def build_title(col):
    """Compose the title given the column (es SD_T)"""
    for sigla,nome in NAMES:
        if sigla in col:
            gender = GENDER[col[3]]
            return nome + " - " + gender
    return 'ERROR'

def build_layout(d19, d20, col):
    # data preparation
    d19avg = d19.groupby('MESE').mean()
    x = np.arange(1,13)

    # extract in order of month
    dx = pd.DataFrame({'MESE':x}).merge(d19avg.reset_index())
    y19 = dx[col].values

    dx = pd.DataFrame({'MESE':x}).merge(d20)
    y20 = dx[col].values

    # bokeh plot
    data = {'Mese': MESI, 'Media': y19, '2020': y20}
    source = ColumnDataSource(data=data)

    hmax = max(max(y19),max(y20))
    p = figure(x_range=MESI, y_range=(0, hmax), height=350,
               title=build_title(col),tools="save,hover",
               tooltips=[("Mese","@Mese"),("Media","@Media"),("2020","@2020")])

    p.vbar(x=dodge('Mese', -0.30, range=p.x_range), top='Media', width=0.3, source=source,
       color=void.color_table['gray'], legend_label="Media")
       #color="#c9d9d3", legend_label="Media")
    p.vbar(x=dodge('Mese', 0.0, range=p.x_range), top='2020', width=0.3, source=source,
       color=void.color_table['blue'], legend_label="2020")
       #color="#718dbf", legend_label="2020")

    p.xaxis.axis_label = 'Mesi'
    p.yaxis.axis_label = 'Decessi'
    p.legend.location = "top_right"
    p.legend.background_fill_alpha = 0.2

    void.setup_fonts(p)

    return p


def load_datasets(datadir):
    import os
    # Dataset San Donà
    df_sandona = pd.read_csv(os.path.join(datadir,'deceduti_SanDona.csv'))
    df_sandona['DataDecesso']=pd.to_datetime(df_sandona['DataDecesso'], format='%d/%m/%Y')
    df_sandona['Comune'] = 'San Donà di Piave'

    # Dataset Jesolo
    df_jesolo = pd.read_csv(os.path.join(datadir,'decessi_Jesolo.csv'))
    df_jesolo['DataDecesso']=pd.to_datetime(df_jesolo['DataDecesso'], format='%d/%m/%Y')
    df_jesolo['Comune'] = 'Jesolo'

    # Dataset Musile
    df_musile = pd.read_csv(os.path.join(datadir,'decessi_Musile.csv'))
    df_musile['DataDecesso']=pd.to_datetime(df_musile['DataDecesso'], format='%Y-%m-%d')
    df_musile['Comune'] = 'Musile di Piave'

    # Dataset Noventa
    df_noventa = pd.read_csv(os.path.join(datadir,'decessi_Noventa.csv'))
    df_noventa['DataDecesso']=pd.to_datetime(df_noventa['DataDecesso'], format='%Y-%m-%d')
    df_noventa['Comune'] = 'Noventa di Piave'

    # Dataset San Stino
    df_sanstino = pd.read_csv(os.path.join(datadir,'decessiSanStino.csv'))
    df_sanstino['DataDecesso']=pd.to_datetime(df_sanstino['DataDecesso'], format='%Y-%m-%d')
    df_sanstino['Comune'] = 'San Stino di Livenza'

    # Dataset Portogruaro
    df_porto = pd.read_csv(os.path.join(datadir,'mortalitaPortogruaro.csv'))
    df_porto['DataDecesso']=pd.to_datetime(df_porto['DataDecesso'], format='%d/%m/%Y')
    df_porto['Comune'] = 'Portogruaro'

    # All together
    df = pd.concat([df_sandona, df_jesolo, df_musile, df_noventa, df_sanstino, df_porto])

    # Tolgo data di nascita e decesso
    df.drop(['DataNascita','EtaDecesso'], axis=1, inplace=True)

    # Aggiungo Colonna Totale, Maschi e Femmine per Comune

    # San Donà
    df['SD_T'] = 0
    df['SD_M'] = 0
    df['SD_F'] = 0
    # Jesolo
    df['JS_T'] = 0
    df['JS_M'] = 0
    df['JS_F'] = 0
    # Musile
    df['MU_T'] = 0
    df['MU_M'] = 0
    df['MU_F'] = 0
    # Noventa
    df['NO_T'] = 0
    df['NO_M'] = 0
    df['NO_F'] = 0
    # San Stino
    df['SS_T'] = 0
    df['SS_M'] = 0
    df['SS_F'] = 0
    # Portogruaro
    df['PO_T'] = 0
    df['PO_M'] = 0
    df['PO_F'] = 0

    # Maschere
    maschi = df['Sesso'] == 'M'
    sandona = df['Comune'] == 'San Donà di Piave'
    jesolo = df['Comune'] == 'Jesolo'
    musile = df['Comune'] == 'Musile di Piave'
    noventa = df['Comune'] == 'Noventa di Piave'
    sanstino = df['Comune'] == 'San Stino di Livenza'
    porto = df['Comune'] == 'Portogruaro'

    # Set maschi/femmine/totali
    df.loc[sandona, 'SD_T'] = 1
    df.loc[sandona & maschi, 'SD_M'] = 1
    df.loc[sandona & ~maschi, 'SD_F'] = 1
    df.loc[jesolo, 'JS_T'] = 1
    df.loc[jesolo & maschi, 'JS_M'] = 1
    df.loc[jesolo & ~maschi, 'JS_F'] = 1
    df.loc[musile, 'MU_T'] = 1
    df.loc[musile & maschi, 'MU_M'] = 1
    df.loc[musile & ~maschi, 'MU_F'] = 1
    df.loc[noventa, 'NO_T'] = 1
    df.loc[noventa & maschi, 'NO_M'] = 1
    df.loc[noventa & ~maschi, 'NO_F'] = 1
    df.loc[sanstino, 'SS_T'] = 1
    df.loc[sanstino & maschi, 'SS_M'] = 1
    df.loc[sanstino & ~maschi, 'SS_F'] = 1
    df.loc[porto, 'PO_T'] = 1
    df.loc[porto & maschi, 'PO_M'] = 1
    df.loc[porto & ~maschi, 'PO_F'] = 1

    # Indice
    df.set_index('DataDecesso', inplace=True)

    return df

COLUMNS = [
    'SD_T',
    'SD_M',
    'SD_F',
    'JS_T',
    'JS_M',
    'JS_F',
    'MU_T',
    'MU_M',
    'MU_F',
    'NO_T',
    'NO_M',
    'NO_F',
    'SS_T',
    'SS_M',
    'SS_F',
    'PO_T',
    'PO_M',
    'PO_F',
] # COLUMNS

def main(datadir, htmlout):

    df = load_datasets(datadir)

    # split into 2 chunks (2000-2019 and 2000 only)
    d19 = df.loc['2000':'2019']
    d19Mtot = d19.resample('M').sum()
    d19Mtot['MESE'] = d19Mtot.index.month

    d20 = df.loc['2020']
    d20Mtot = d20.resample('M').sum()
    d20Mtot['MESE'] = d20Mtot.index.month

    # build the HTML

    with open('template.html', 'r') as ftempl:
        htmltempl = ftempl.read()

        for col in COLUMNS:
            layout = build_layout(d19Mtot, d20Mtot, col)

            script, div = components(layout)
            htmltempl = htmltempl.replace("$BOKEH_DIV_"+col+"$", div)
            htmltempl = htmltempl.replace("$BOKEH_SCRIPT_"+col+"$", script)

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
