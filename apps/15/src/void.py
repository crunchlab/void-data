"""
Veneto Orientale Innovation Lab

Modulo con gli elementi comuni per l'elaborazione dei dati
"""

from bokeh.colors import RGB

# void colors
color_table = {
        "blue":   RGB(72,159,223),
        "green":  RGB(44,200,77),
        "red":    RGB(238,56,49),
        "gray":   RGB(229, 205,230),
        "yellow": RGB(246, 183, 0),
        "black":  RGB(45, 41, 38),
        "pink":   RGB(255, 182, 193),
        "light_blue": RGB(173, 216, 230),
}

palette5 = (
        color_table["gray"],
        color_table["green"],
        color_table["blue"],
        color_table["yellow"],
        color_table["red"],
)

# void font
font_family = "Work Sans"

def setup_fonts(plot):
    """Imposta i font degli assi e del titolo"""

    plot.title.text_font = font_family
    plot.title.align = 'center'
    plot.title.text_font_size = '21px'
    #p.title.text_font_style = 'bold'
    plot.xaxis.axis_label_text_font = font_family
    plot.yaxis.axis_label_text_font = font_family
    plot.legend.label_text_font = font_family

    return plot

# utils
months_labels = {
    1: "Gen", 2:"Feb", 3: "Mar", 4: "Apr", 5: "Mag", 6: "Giu",
    7: "Lug", 8: "Ago", 9: "Set", 10: "Ott", 11: "Nov", 12: "Dic"
}
