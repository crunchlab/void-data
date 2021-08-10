# VOID Open Data Repository
Repository dei codici sorgenti e del sito della parte Open Data del progetto
Veneto Orientale Innovation District.

## Apps
Ogni cartella contiene i sorgenti Python e tutto il necessario per creare 
l'html che va a comporre il sito. I dataset vanno recuperati dal portale
della [Regione Veneto](https://dati.veneto.it/).

L'esecuzione degli script richiede Python 3.6 o superiore e le seguenti
librerie (non per tutte le app):

- numpy==1.19.4
- pandas==1.1.4
- bokeh==2.3.1
- holoviews==1.14.3
- networkx==2.5.1
- scikit-learn==0.24.1
- matplotlib==3.3.4

## Site
Nella directory `site` viene riportata la struttura del sito statico
renderizzato e completato partendo dagli output delle apps.

All'interno del sito sono presenti anche le infografiche in formato PDF.

## Infografiche
Nella directory `infografiche` sono presenti le infografiche statiche in PDF.
