import numpy as np
import matplotlib.pyplot as plt
import math

class ToolTipOnHover(object):
    def __init__(self, data, labels):
        self.data = data

        self.annotations = []
        for xy, l in zip(data, labels):
            annotation = plt.annotate(unicode(l,'utf8'),
                xy=xy, xycoords='data',
                xytext=(10, 5), textcoords='offset points',
                horizontalalignment="left",
                bbox=dict(boxstyle="round", facecolor="w",
                          edgecolor="0.5", alpha=0.9)
            )
            # by default, disable the annotation visibility
            annotation.set_visible(False)
            self.annotations.append(annotation)

    def attachTo(self, figure):
        for a in self.annotations:
            a.set_figure(figure)

        ax = figure.gca()

        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        self.xradius = (xlim[1] - xlim[0]) / 100.0
        self.yradius = (ylim[1] - ylim[0]) / 100.0

        figure.canvas.mpl_connect('motion_notify_event', self._onMotion)

    def _onMotion(self, event):
        if event.xdata and event.ydata:
            min_dist = float("inf")
            closest = -1

            for i, sample in enumerate(self.data):
                dist = math.sqrt((event.xdata - sample[0])**2 + (event.ydata - sample[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    closest = i

            visibility_changed = False
            for i, sample in enumerate(self.data):
                should_be_visible = (abs(event.xdata - sample[0]) < self.xradius and abs(event.ydata - sample[1]) < self.yradius and i == closest)

                annotation = self.annotations[i]
                if should_be_visible != annotation.get_visible():
                    visibility_changed = True
                    annotation.set_visible(should_be_visible)

            if visibility_changed:
                plt.draw()


def main():
    data = np.random.rand(10, 2)
    labels = [str(i) for i in xrange(10)]

    plt.scatter(data[:,0], data[:,1])
    fig = plt.gcf()

    tooltip = ToolTipOnHover(data, labels)
    tooltip.attachTo(fig)

    plt.show()

if __name__ == '__main__':
    main()







