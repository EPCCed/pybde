import matplotlib.pyplot as plt
import numpy as np


class SwitchPoints:

    def __init__(self, t, y, end, label=None, style=None):
        self.t = t
        self.y = y
        self.end = end
        self.label = label
        self.style = style

    def cut(self, new_end):
        res_t = []
        res_y = []
        for i, tt in enumerate(self.t):
            if tt <= new_end:     # TODO - do a proper comparison
                res_t.append(tt)
                res_y.append(self.y[i])

        return SwitchPoints(res_t, res_y, new_end)

    def compress(self, x, y):  # Remove redundant switch points
        previous_y = None
        res_t = []
        res_y = []
        for i, yy in enumerate(self.y):
            if yy != previous_y:
                res_t.append(self.t[i])
                res_y.append(yy)
                previous_y = yy
        self.t = res_t
        self.y = res_y

    def plot(self, offset=0):
        plot_t, plot_y = self.to_plot_data(offset=offset)
        if self.style:
            plt.plot(plot_t, plot_y, self.style, label=self.label)
        else:
            plt.plot(plot_t, plot_y, label=self.label)

    def show(self, offset=0):
        plot_t, plot_y = self.to_plot_data(offset=offset)
        if self.style:
            plt.plot(plot_t, plot_y, self.style, label=self.label)
        else:
            plt.plot(plot_t, plot_y, label=self.label)
        plt.xlabel('time')
        plt.yticks([0, 1])
        plt.grid(True)
        plt.tight_layout()

    def to_plot_data(self, offset=0):
        res_t = []
        res_y = []

        res_t = [self.t[0]]
        for i in range(1, len(self.t)):
            res_t.append(self.t[i])
            res_t.append(self.t[i])
        if self.t[-1] < self.end and not np.isclose(self.t[-1], self.end):
            res_t.append(self.end)

        for i in range(len(self.y)-1):
            res_y.append(self.y[i] + offset)
            res_y.append(self.y[i] + offset)
        res_y.append(self.y[-1] + offset)
        if self.t[-1] < self.end and not np.isclose(self.t[-1], self.end):
            res_y.append(self.y[-1] + offset)

        return res_t, res_y

    @staticmethod
    def plot_many(list_of_switch_points):
        for i, switch_points in enumerate(list_of_switch_points):
            switch_points.plot(offset=0.1*i)  # todo better handle the offset decision
        plt.xlabel('time')
        plt.yticks([0, 1])
        plt.grid(True)
        plt.tight_layout()

    @staticmethod
    def show_many(list_of_switch_points):
        SwitchPoints.plot_many(list_of_switch_points)
        plt.show()

    @staticmethod
    def to_logical(t, y, end):
        new_y = (np.array(y) > 0).tolist()
        return SwitchPoints(t, new_y, end)

    @staticmethod
    def to_discrete(t, y):
        # This is very basic version
        res_x = x.tolist()

        mn = y.min(axis=0)
        mx = y.max(axis=0)

        foo = (y - mn) / (mx - mn)

        bar = (foo > 0.5)  # TODO: take in this as a threshold parameter

        res_y = bar.tolist()

        result = SwitchPoints(res_x, res_y)

        return result.compress()
