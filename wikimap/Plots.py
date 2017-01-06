import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

def createDegreePlot(data):
    width = 0.8
    xs = [i - (width / 2) for i in xrange(len(data))]
    plt.bar(xs, data, width=width)
    plt.xlabel('Degree', fontsize=14)
    plt.ylabel('Count', fontsize=14)
    plt.title('Number of points by their degree in the graph spanned by links', fontsize=14)
    plt.xlim([-1, len(data)])
    return plt.gcf()
