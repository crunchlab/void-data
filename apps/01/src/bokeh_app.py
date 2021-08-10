from bokeh_decessi import build_layout as decessi
from bokeh_mesi import build_layout as mesi

from bokeh.embed import components

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('htmlfile', type=str)

    args = parser.parse_args()

    inf = "dataset.csv"
    outf = args.htmlfile

    layout_decessi = decessi(inf)
    layout_mesi = mesi(inf)

    with open('template.html', 'r') as ftempl:
        htmltempl = ftempl.read()

        script, div = components(layout_decessi)
        htmltempl = htmltempl.replace('$BOKEH_DIV_FASCE$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_FASCE$', script)

        script, div = components(layout_mesi)
        htmltempl = htmltempl.replace('$BOKEH_DIV_MESI$', div)
        htmltempl = htmltempl.replace('$BOKEH_SCRIPT_MESI$', script)

        with open(outf, 'w') as fout:
            fout.write(htmltempl)

