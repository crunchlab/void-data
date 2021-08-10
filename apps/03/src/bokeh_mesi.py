#!/usr/bin/env python
# coding: utf-8

# # Analisi su base Mensile della mortalità

# Import Packages
import void
import pandas as pd
import numpy as np
import argparse

from bokeh.plotting import figure
from bokeh.models import HoverTool
from bokeh.embed import components
from bokeh.models import Legend

# sesso;data nascita;data decesso;eta decesso
c_sesso = "sesso"
c_dt_nascita = "data nascita"
c_dt_decesso = "data decesso"
c_eta = "eta decesso"

def build_layout(inf):

    # DECEDUTI
    df = pd.read_csv(inf, sep=';')
    df[c_dt_nascita] = pd.to_datetime(df[c_dt_nascita], format='%Y-%m-%d')
    df[c_dt_decesso] = pd.to_datetime(df[c_dt_decesso], format='%Y-%m-%d')
#    df = df.drop(['Cognome','Nome'],axis=1)
    # Calculate Age
#    days = df[c_dt_decesso] - df[c_dt_nascita]
#    years = days / np.timedelta64(1, 'Y')
#    df[c_eta] = np.floor(years).astype('int')
    df.index = df[c_dt_decesso]


    # Remove 2021
#    df = df.drop(df.loc['2021'].index)

    # Remove the 2020 and take apart
    df2020 = df.loc['2020']
    df = df.loc[:'2019']

    df['cnt'] = 1
    dfmonth = df.resample('M').sum()

    dfmonth['mese'] = dfmonth.index.month
    dfmonth = dfmonth.drop([c_eta], axis=1)

    # Create the dataset to plot
    groups = dfmonth.groupby('mese')
    q1 = groups.quantile(q=0.25)
    q2 = groups.quantile(q=0.5)
    q3 = groups.quantile(q=0.75)

    #groups.describe()

    # Value of 2020
    df2020['cnt'] = 1
    df2020m = df2020.resample('M').sum()

    df2020m['mese'] = df2020m.index.month
    df2020m = df2020m.drop([c_eta], axis=1)
    df2020m


    # # Box Plot

    def month_to_cats(months):
        return [void.months_labels[m] for m in months]
        #return [str(m) for m in months]


    cats = month_to_cats(range(1,13))
    iqr = q3 - q1
    upper = q3 + 1.5*iqr
    lower = q1 - 1.5*iqr

    # find the outliers for each category
    def outliers(group):
        cat = group.name
        return group[(group.cnt > upper.loc[cat]['cnt']) | (group.cnt < lower.loc[cat]['cnt'])]['cnt']

    out = groups.apply(outliers).dropna()


    if not out.empty:
        outx = month_to_cats(out.index.get_level_values(0))
        outy = list(out.values)

    # if no outliers, shrink lengths of stems to be no longer than the minimums or maximums
    qmin = groups.quantile(q=0.00)
    qmax = groups.quantile(q=1.00)
    upper.cnt = [min([x,y]) for (x,y) in zip(list(qmax.loc[:,'cnt']),upper.cnt)]
    lower.cnt = [max([x,y]) for (x,y) in zip(list(qmin.loc[:,'cnt']),lower.cnt)]


    p = figure(x_range=cats, plot_width=800, plot_height=400,
            title="DISTRIBUZIONE DECESSI MENSILE 2000-2019 vs. 2020")
    # stems
    p.segment(cats, upper.cnt, cats, q3.cnt, line_color=void.color_table["black"])
    p.segment(cats, lower.cnt, cats, q1.cnt, line_color=void.color_table["black"])

    # boxes
    p.vbar(cats, 0.3, q2.cnt, q3.cnt, fill_color=void.color_table["green"],
            line_color=void.color_table["black"])
    p.vbar(cats, 0.3, q1.cnt, q2.cnt, fill_color=void.color_table["blue"],
            line_color=void.color_table["black"])

    # whiskers (almost-0 height rects simpler than segments)
    p.rect(cats, lower.cnt, 0.2, 0.01, line_color=void.color_table["black"])
    p.rect(cats, upper.cnt, 0.2, 0.01, line_color=void.color_table["black"])

    # outliers
    rend_outlier = None
    if not out.empty:
        rend_outlier = p.circle(outx, outy, size=6, color=void.color_table["gray"],
                fill_alpha=0.6)

    # 2020
    rend_2020 = p.circle(month_to_cats(df2020m['mese'].values),
            df2020m['cnt'].values, size=6,
            color=void.color_table["red"], fill_alpha=0.6)

    p.line(month_to_cats(df2020m['mese'].values), df2020m['cnt'].values,
            color=void.color_table["red"])


    hover = HoverTool()
    hover.tooltips = [
        ("Decessi", "$y")
    ]

    #p.toolbar.active_inspect = hover
    p.add_tools(hover)

    #p.legend.location = 'bottom_right'
    legend = Legend(items=[
        ("Outlier/Anomalo", [rend_outlier]),
        ("Anno 2020", [rend_2020])
    ], location=(0, 0))

    p.add_layout(legend, 'right')

    p.xaxis.axis_label = 'Mese'
    p.yaxis.axis_label = 'Decessi'

    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = void.color_table["gray"]
    #p.grid.grid_line_width = 2
    #p.xaxis.major_label_text_font_size="16px"

    void.setup_fonts(p)

    return p
