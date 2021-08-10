#!/usr/bin/env python
# coding: utf-8

import void

import pandas as pd
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Deceduti Normalizzati e Trendline")
parser.add_argument('csvres', type=str)
parser.add_argument('csvdec', type=str)
parser.add_argument('htmlfile', type=str)

args = parser.parse_args()

decedutif = 'data/dataset.csv'
#decedutif = args.csvdec
residentif = 'data/residenti.csv'
#residentif = args.csvres
outf = args.htmlfile

# RESIDENTI
dfres = pd.read_csv(residentif)
dfres['data'] = pd.to_datetime(dfres['data'], dayfirst=True)
dfres.index = dfres['data']
dfres

# DECEDUTI
df = pd.read_csv(decedutif)
df['DataNascita'] = pd.to_datetime(df['DataNascita'], dayfirst=True)
df['DataDecesso'] = pd.to_datetime(df['DataDecesso'], dayfirst=True)
df = df.drop(['Cognome','Nome'],axis=1)

# Calculate Age
days = df['DataDecesso'] - df['DataNascita']
years = days / np.timedelta64(1, 'Y')
df['EtaDecesso'] = np.floor(years).astype('int')
df.index = df['DataDecesso']
df

# DECEDUTI PER ANNO
dfdec = df['EtaDecesso'].resample('AS').count()
dfdec

# DECEDUTI NORMALIZZATI SULLA POPOLAZIONE
dfyear = pd.concat([dfdec, dfres], axis=1)
dfyear['decessi'] = dfyear['EtaDecesso']
dfyear = dfyear.drop(['EtaDecesso'], axis=1)
dfyear['ratio'] = dfyear['decessi'] / dfyear['residenti']
dfyear['perc'] = dfyear['ratio'] * 1000
dfyear

# Remove 2021
dfyear = dfyear.drop(dfyear.loc['2021'].index)

# exclude the 2020 from train set because it's the year to test
dftrain = dfyear.loc[:'2019']
# [:, None] to have the right dimension fot fit [sample, features]
x_train = dftrain.index.year.values[:, None]
y_train = dftrain['perc'].values[:, None]


# TRENDLINE
from sklearn import linear_model

reg = linear_model.LinearRegression()
reg.fit(x_train, y_train)
reg.get_params()

# tolleranza
reg.score(x_train, y_train)

# predict 2021
perc2021 = reg.predict([[2020]])
perc2021

# trend
years = dfyear.index.year.values[:, None]
trends = reg.predict(years)
trends = trends.flatten()

# # CHART
from datetime import timedelta
from bokeh.plotting import figure, output_file, save, show
from bokeh.models import ColumnDataSource
from bokeh.palettes import small_palettes
from bokeh.models import Legend
from bokeh.layouts import row, column
from bokeh.embed import components

dfyear20 = dfyear.loc['2020']

source = ColumnDataSource(dfyear)
source20 = ColumnDataSource(dfyear20)

p = figure(plot_width=800, plot_height=400, x_axis_type="datetime",
           title="INCIDENZA DECESSI")
# all data in yellow
p.vbar(top="perc", x='data',
            width=timedelta(days=180),
            color=void.color_table["yellow"],
            source=source)
# remark 2020 in red
p.vbar(top="perc", x='data',
            width=timedelta(days=180),
            color=void.color_table["red"],
            source=source20)
#trendline
p.line(dfyear.index, trends, color=void.color_table["black"], alpha=1.0, width=2)

p.xaxis.axis_label = 'Anno'
p.yaxis.axis_label = 'Decessi per mille abitanti'

void.setup_fonts(p)

script, div = components(p)

with open('template.html', 'r') as ftempl:
    htmltempl = ftempl.read()
    htmltempl = htmltempl.replace('$BOKEH_DIV$', div)
    htmltempl = htmltempl.replace('$BOKEH_SCRIPT$', script)
    with open(outf, 'w') as fout:
        fout.write(htmltempl)

