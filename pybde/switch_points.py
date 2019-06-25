import matplotlib.pyplot as plt
import numpy as np
import math

class SwitchPoints:

    rel_tol = 1e-09
    abs_tol = 0.0

    @staticmethod
    def times_are_equal(t1, t2):
        """
        Compares if two times are equal within tolerance.

        Parameters
        ----------

        t1 : float
            A time point.
        t2 : float
            A time point.

        Returns
        -------

        bool
            True if the two times are equal, False otherwise.
        """
        return math.isclose(t1, t2, rel_tol=SwitchPoints.rel_tol, abs_tol=SwitchPoints.abs_tol)

    @staticmethod
    def is_time_before(t1, t2):
        """
        Tests if the given time is before or equal to the simulation end time.

        Parameters
        ---------

        t : float
            A time point.

        Returns
        -------

        bool
            True if the time is before or equal to the end point.

        """
        if t1 < t2 and not SwitchPoints.times_are_equal(t1, t2):
            return True

    @staticmethod
    def is_time_before_or_equal(t1, t2):
        """
        Tests if the given time is before or equal to the simulation end time.

        Parameters
        ---------

        t : float
            A time point.

        Returns
        -------

        bool
            True if the time is before or equal to the end point.

        """
        if t1 < t2 or SwitchPoints.times_are_equal(t1, t2):
            return True

    def __init__(self, t, y, end, label=None, style=None):
        self.t = t
        self.y = y
        self.end = end
        self.label = label
        self.style = style

        # Pad out the state values to be the length of the inputs
        while len(y) < len(t):
            y.append(not y[-1])

        if len(y) > len(t):
            raise ValueError("Cannot specify more value elements (y) that time elements (t).")

        for i in range(len(t)-1):
            if t[i] >= t[i+1]:
                raise ValueError("Time values (t) must be incrementing.")

        if end < t[-1]:
            raise ValueError("End time must be equal to or greater than last switch time")

    def cut(self, new_start, new_end, keep_switch_on_end=False):
        res_t = []
        res_y = []

        if SwitchPoints.is_time_before_or_equal(new_end, new_start):
            raise ValueError("End cut time cannot be before start cut time")

        # Error if cut out of range
        if SwitchPoints.is_time_before(new_start, self.t[0]):
            raise ValueError("Cannot cut from a value before the start.")

        # Find the start
        if SwitchPoints.is_time_before(self.end, new_end):
            raise ValueError("Cannot cut to a value after the end.")

        for i, tt in enumerate(self.t):
            if SwitchPoints.is_time_before_or_equal(new_start, tt):
                if SwitchPoints.is_time_before(tt, new_end) or \
                        (keep_switch_on_end and SwitchPoints.times_are_equal(tt, new_end)):
                    if len(res_t) == 0 and not SwitchPoints.times_are_equal(new_start, tt):
                        res_t.append(new_start)
                        res_y.append(last_state_before_start)
                    res_t.append(tt)
                    res_y.append(self.y[i])
            else:
                last_state_before_start = self.y[i]

        # If we have no switch points then add a single state at the start
        if len(res_t) == 0:
            res_t.append(new_start)
            res_y.append(last_state_before_start)

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
    def plot_many(list_of_switch_points, offset=0.05):
        for i, switch_points in enumerate(list_of_switch_points):
            switch_points.plot(offset=offset*i)
        plt.yticks([0, 1])
        plt.grid(True)
        plt.tight_layout()

    @staticmethod
    def show_many(list_of_switch_points, offset=0.05):
        SwitchPoints.plot_many(list_of_switch_points, offset=offset)
        plt.show()

    @staticmethod
    def absolute_threshold(t, y, threshold):
        t = np.array(t)
        y = np.array(y)
        res_x = [t[0]]

        # If start on the threshold then look ahead to see the first state value
        initial_state = False  # Default state if all data is on the threshold plateau
        prev = 0
        for i, yy in enumerate(y):
            if y[i] != threshold:
                initial_state = y[i] > threshold
                prev = i
                break

        print("t = {} y = {}".format(t,y))
        for i in range(1, len(t)):
            v = (y[prev] - threshold) * (y[i] - threshold)
            print("i = {} prev = {} v = {}".format(i, prev, v))
            if v < 0:
                # We have a threshold crossing - interpolate where it crosses
                if prev == i-1:
                    m = (y[i]-y[prev])/(t[i]-t[prev])
                    c = y[i] - m * t[i]
                    intercept = (threshold-c)/m
                    res_x.append(intercept)
                else:
                    # We're exiting a plateau
                    res_x.append((t[i] - t[prev])/2)
                prev = i
            elif v > 0:
                prev = i

        return SwitchPoints(res_x, [initial_state], t[-1])

    @staticmethod
    def relative_threshold(t, y, threshold):
        t = np.array(t)
        y = np.array(y)
        mn = y.min(axis=0)
        mx = y.max(axis=0)
        return SwitchPoints.absolute_threshold(t, y, mn + threshold * (mx-mn) )

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

        # Check all inputs have same start time
        for i in range(len(inputs)-1):
            if inputs[i].t[0] != inputs[i+1].t[0]:
                raise ValueError("Cannot merge inputs with different start times")

        x = [inputs[0].t[0]]
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

        if self.end != other.end or self.t[0] != other.t[0]:
            raise ValueError("Can only calculate Hamming distance over identical ranges.")
        distance = 0.0

        times, states = SwitchPoints.merge([self, other])
        times.append(self.end)

        for i, state in enumerate(states):
            if state[0] != state[1]:
                distance += times[i+1] - times[i]

        return distance
