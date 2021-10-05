import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import holoviews as hv
from holoviews import opts, dim
from bokeh.models import HoverTool
hv.extension('bokeh')
from bokeh.embed import components
#from bokeh.io import export_png

def build_layout(df, enc, name="sankey"):
    """
    Create the Sankey diagram from the dataframe, using the encoding for the
    labels

    Parameters
    ===========
    df: DataFrame
    enc: LabelEncoder

    """

    nodes = hv.Dataset(enumerate(enc.classes_), 'index', 'label')
    edges = df[['FROM_INDEX','TO_INDEX','Flusso']].to_records(index=False)
    # avoid type issues
    edges = [tuple(e) for e in edges]


    sankey = hv.Sankey((edges, nodes), ['From', 'To'])

    sankey.opts(
        opts.Sankey(labels='label',
                    label_position='outer',
                    show_values=False,
                    width=800,
                    height=600,
                    cmap='Set3',
                    edge_color=dim('From').str(),
                    node_color=dim('index').str()))


    # Save Interactive image only
    renderer = hv.renderer('bokeh')

    layout = renderer.get_plot_state(sankey)

    # workaround to remove "from" and "to", useless
    layout.tools[0].tooltips = [layout.tools[0].tooltips[-1]]

#    export_png(layout, filename="%s.png" % name, width=1600, height=1200)

    return layout

def get_national(df):
    """
    Extracts the dataframe of the national migrations and the encorder for the
    name of the Comuni

    Parameter
    ===========
    df: DataFrame

    Returns
    ========
    g_c: DataFrame['FROM_INDEX','TO_INDEX','Flusso']
    com_enc: LabelEncoder
    """

    df_c = df[df['STATO PROVENIENZA']=='ITALIA']

    # Raggruppa per Comune di Provenienza
    g_c = df_c.groupby('COMUNE PROVENIENZA').size().reset_index(name='Flusso')

    # Aggiungi Colonna Comune di Destinazione
    g_c['COMUNE DESTINAZIONE'] = 'JESOLO'

    # Filter
    g_c = g_c[g_c['Flusso']>=60]

    # Encoding
    com_enc = LabelEncoder()

    cp = g_c['COMUNE PROVENIENZA'].values
    cd = g_c['COMUNE DESTINAZIONE'].values
    all_comuni = np.concatenate((cp, cd), axis=None)

    com_enc.fit(all_comuni)

    g_c['FROM_INDEX'] = com_enc.transform(g_c['COMUNE PROVENIENZA'])
    g_c['TO_INDEX'] = com_enc.transform(g_c['COMUNE DESTINAZIONE'])

    # Exclude loops
    g_c = g_c[g_c['COMUNE PROVENIENZA'] != g_c['COMUNE DESTINAZIONE']]

    return g_c, com_enc

def get_international(df):
    """
    Extracts the dataframe of the international migrations and the encorder for the
    name of the States

    Parameter
    ===========
    df: DataFrame

    Returns
    ========
    g_c: DataFrame['FROM_INDEX','TO_INDEX','Flusso']
    com_enc: LabelEncoder
    """

    df_s = df[df['STATO PROVENIENZA']!='ITALIA']
    # Raggruppa per Stato di Provenienza
    g_s = df_s.groupby('STATO PROVENIENZA').size().reset_index(name='Flusso')

    # Aggiungi Colonna Comune di Destinazione
    g_s['COMUNE DESTINAZIONE'] = 'JESOLO'
    # Filtra
    g_s = g_s[g_s['Flusso']>=50]

    # Encoding
    st_enc = LabelEncoder()

    cp = g_s['STATO PROVENIENZA'].values
    cd = g_s['COMUNE DESTINAZIONE'].values
    all_comuni = np.concatenate((cp, cd), axis=None)

    st_enc.fit(all_comuni)

    g_s['FROM_INDEX'] = st_enc.transform(g_s['STATO PROVENIENZA'])
    g_s['TO_INDEX'] = st_enc.transform(g_s['COMUNE DESTINAZIONE'])


    return g_s, st_enc


def main(datafile, htmlout):

    # read the data and prepare the dataframe
    df = pd.read_csv(datafile)

    # Build the chart for national migration
    g_c, com_enc = get_national(df)
    lay_nat = build_layout(g_c, com_enc, name="italia")

    # Build the chart for international migration
    g_c, com_enc = get_international(df)
    lay_inter = build_layout(g_c, com_enc, name="stranieri")

    # to html

    with open('template.html', 'r') as ftempl:
        htmltempl = ftempl.read()

        script, div = components(lay_nat)
        htmltempl = htmltempl.replace('$BOKEH_DIV_NAT$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_NAT$', script)

        script, div = components(lay_inter)
        htmltempl = htmltempl.replace('$BOKEH_DIV_INTER$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_INTER$', script)

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

#    datafile = 'data/anagrafe_jesolo.csv'
#    htmlout = 'index.html'

    main(datafile, htmlout)
