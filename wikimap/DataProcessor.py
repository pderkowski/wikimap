import pandas as pd

def buildFinalTable(tsnePath, dictionaryPath, finalPath):
    tsne = pd.read_table(tsnePath, delim_whitespace=True, header=None, names=['id', 'x', 'y'])
    dictionary = pd.read_table(dictionaryPath, delim_whitespace=True, header=None, names=['id', 'title'])
    joined = tsne.reset_index().merge(dictionary, how='inner', on='id', sort=False).set_index('index')
    cols = ['x', 'y', 'title']
    joined.info()
    joined = joined[cols]
    joined.to_csv(finalPath, sep=' ', header=None, cols=cols, index=False)