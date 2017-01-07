import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

def createDegreePlot(data, maxDegree=30):
    ys = [0] * (maxDegree + 1)
    for d in data:
        print d[0], ' ', d[1]
        ys[d[0]] = d[1]

    width = 0.8
    xs = [x - (width / 2) for x in xrange(maxDegree + 1)]
    plt.bar(xs, ys, width=width)
    plt.xlabel('Degree', fontsize=14)
    plt.ylabel('Count', fontsize=14)
    plt.title('Number of points by their degree in the graph spanned by links', fontsize=14)
    plt.xlim([-1, maxDegree + 1])
    return plt.gcf()

def createPointOrdersPlot(pointOrders):
    pointOrders = list(pointOrders)

    bins = 1 + int(max(pointOrders) / 1000)
    plt.hist(pointOrders, bins=bins)
    plt.xlabel('Pagerank order', fontsize=14)
    plt.ylabel('Count', fontsize=14)
    return plt.gcf()
