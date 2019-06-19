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

        return SwitchPoints(res_t, res_y, new_end, label=self.label, style=self.style)

    def compress(self):  # Remove redundant switch points
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

        return self

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
            switch_points.plot(offset=0.05*i)  # todo better handle the offset decision
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
        res_x = t.tolist()

        mn = y.min(axis=0)
        mx = y.max(axis=0)

        foo = (y - mn) / (mx - mn)

        bar = (foo > 0.5)  # TODO: take in this as a threshold parameter

        res_y = bar.tolist()

        result = SwitchPoints(res_x, res_y, res_x[-1])

        return result.compress()

    @staticmethod
    def merge(inputs):
        x = [0]
        y = []
        indexes = [0] * len(inputs)
        y.append(SwitchPoints._get_state(indexes, inputs))
        t, indexes = SwitchPoints._get_next_time(indexes, inputs)
        while t:
            x.append(t)
            y.append(SwitchPoints._get_state(indexes, inputs))
            t, indexes = SwitchPoints._get_next_time(indexes, inputs)

        return x, y

    @staticmethod
    def _get_state(indexes, inputs):
        state = []
        for i in range(len(indexes)):
            state.append(inputs[i].y[indexes[i]])
        return state

    @staticmethod
    def _get_next_time(indexes, inputs):
        times = []
        t = None
        for i in range(len(indexes)):
            if indexes[i] + 1 < len(inputs[i].t):
                times.append(inputs[i].t[indexes[i] + 1])
        if len(times) == 0:
            return None, None
        else:
            t = min(times)

        # Now update the indexes
        for i in range(len(indexes)):
            if indexes[i] + 1 < len(inputs[i].t):
                if t >= inputs[i].t[indexes[i]+1]:  # TODO Need to do better comparisons here
                    indexes[i] = indexes[i]+1

        return t, indexes

    @staticmethod
    def unmerge(x, y, end):
        result = []
        num_values = len(y[0])
        for i in range(num_values):
            y_data = []
            for yy in y:
                y_data.append(yy[i])
            result.append(SwitchPoints(x, y_data, end).compress())

        return result

    def hamming_distance(self, other):
        distance = 0.0

        times, states = SwitchPoints.merge([self, other])
        times.append(self.end)

        for i, state in enumerate(states):
            if state[0] != state[1]:
                distance += times[i+1] - times[i]

        return distance
