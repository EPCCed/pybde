from enum import IntEnum
import heapq
import numpy as np
import matplotlib.pyplot as plt

# Format of user defined function
#
# fun(Z)
#  Z is a list of list - first index is delay, second is variable
#  so Z[0][2]  is the values of the 3rd variable at the 1st delay
#
# If forcing inputs are used then a second argument Z2 is passed.
# The indexes are the same except they refer to the forcing inputs.

class IndexType(IntEnum):
    VARIABLE = 1
    FORCED_INPUT = 2
    NONE = 3


class CandidateSwitchFinder:

    def __init__(self, delays, x, start, end, forced_x=None):
        self.start = start
        self.end = end
        self.delays = delays

        self.indices = [0] * len(delays)
        self.have_forced_inputs = (forced_x is not None)
        if self.have_forced_inputs:
            self.forced_indices = [0] * len(delays)
        self.times = []

        for i in range(len(self.delays)):
            d = self.delays[i]
            for j in range(len(x)):
                t = x[j]
                if (t + d) <= end:                # Comparing floats occurs here - think about this
                    heapq.heappush(self.times, (t + d, i, IndexType.VARIABLE, j))
                    print("#### adding {}, {}, {}, {} - now have {}".format(t + d, i, IndexType.VARIABLE, j, self.times))

            if self.have_forced_inputs:
                for j in range(len(forced_x)):
                    t = forced_x[j]
                    if (t + d) <= end:                  # COMPARE TIMES HERE - HERE WE DON'T KNOW THE INDEX
                        heapq.heappush(self.times, (t + d, i, IndexType.FORCED_INPUT, j))

        # pop all the indexes until start - this gets all the index correct before start
        self.pop_until_start(start)

        # Add the start time in case it is not a candidate - give it no new index information
        heapq.heappush(self.times, (start, -1, IndexType.NONE, -1))


    def add_new_times(self, t, variable_state_index):
        for i in range(0, len(self.delays)):
            new_time = self.delays[i] + t
            if new_time <= self.end:                   # COMPARE TIMES HERE
                heapq.heappush(self.times, (new_time, i, IndexType.VARIABLE, variable_state_index) )

    def get_next_time(self):

        print("--> In get_next_time:  heapq is : {}".format(self.times))
        if len(self.times) > 0:
            next_time = self.pop_and_update_indices()

            print("--> In get_next_time:  next_time is : {}".format(next_time))

            while len(self.times) > 0 and CandidateSwitchFinder.times_are_equal(self.times[0][0], next_time):
                self.pop_and_update_indices()

            return next_time
        else:
            return None

    @staticmethod
    def times_are_equal(t1, t2):
        return t1 == t2                                   # COMPARE TIMES

    def pop_until_start(self, start):
        while len(self.times) > 0 and self.times[0][0] < start:      # COMPARE TIMES
            self.pop_and_update_indices()

    def pop_and_update_indices(self):
        next_time, delay_index, index_type, state_index = heapq.heappop(self.times)

        print("--> In pop_and_update_indices :  popped : {}, {}, {}, {}".format(next_time, delay_index, index_type, state_index ))

        if index_type == IndexType.VARIABLE:
            self.indices[delay_index] = state_index
        elif index_type == IndexType.FORCED_INPUT:
            self.forced_indices[delay_index] = state_index

        print("--> In pop_and_update_indices :  indices are : {}".format(self.indices))

        return next_time

    def print_state(self):
        print("== Candidate switches ==")
        print("  {}".format(self.times))

class BDESolver:

    def __init__(self,func,delays,x,y, forced_x=None, forced_y=None):

        self.func = func
        self.delays = delays
        self.x = x
        self.y = y

        self.have_forced_inputs = (forced_x is not None)
        self.forced_x = forced_x
        self.forced_y = forced_y

        self.res_x = None
        self.res_y = None
        self.start_x = None
        self.end_x = None

        # TODO - verify stuff
        # x and y arrays are the same length
        # forced x and y are the same length
        # all state list are the same length

    def solve(self, start, end):

        if start < max(self.delays):
            raise ValueError("start_time ({}) must be greater than or equal to the maximum delay ({}).".format(
                start, max(self.delays)))

        if start <= self.x[-1]:
            raise ValueError("start_time ({}) must be greater than final input time ({}).".format(
                start, self.x[-1]))

        # TODO: Throw value error if:
        # start is after end

        self.end_x = end
        self.start_x = start

        # Result arrays - we start with the given history
        self.res_x = self.x.copy()
        self.res_y = self.y.copy()

        candidate_switch_finder = CandidateSwitchFinder(self.delays,self.x,self.start_x, self.end_x,self.forced_x)

        t = candidate_switch_finder.get_next_time()
        while t is not None:
            print("t={}".format(t))
            Z = []
            for i in candidate_switch_finder.indices:
                print("Index i = {} of res_y = {}".format(i, self.res_y))
                Z.append(self.res_y[i])
            
            if not self.have_forced_inputs:
                print("Z {}".format(Z))
                new_state = self.func(Z)
                print("*** at t={} state is {}".format(t,new_state))
            else:
                Z2 = []
                for i in candidate_switch_finder.forced_indices:
                    Z2.append(self.forced_y[i])
                print("Z {} Z2 {}".format(Z,Z2))
                new_state = self.func(Z,Z2)
                print("*** at t={} state is {}".format(t,new_state))

            # Keep this state if it has changed or this is the end of the simulation
            if new_state != self.res_y[-1] or t == self.end_x:
                print("State has changed so adding new state: {}".format(new_state))
                self.res_x.append(t)
                self.res_y.append(new_state)
                candidate_switch_finder.add_new_times(t, len(self.res_x)-1)
            else:
                print("State hasn't changed so not adding it")

            candidate_switch_finder.print_state()
            t = candidate_switch_finder.get_next_time()
            
        # If the last result is not the end time then add it in
        if self.res_x[-1] != self.end_x:                     # COMPARING TIMES HERE
            self.res_x.append(self.end_x)
            self.res_y.append(self.res_y[-1])

    @staticmethod
    def to_logical(x):
        """Coverts integer numpy arrays to logical numpy arrays."""
        return (np.array(x) > 0).tolist()

    @staticmethod
    def to_plot(x, y):
        res_x = [x[0]]
        res_y = [y[0]]
        for i in range(1, len(x)):
            res_x.append(x[i])
            res_y.append(y[i-1])
            res_x.append(x[i])
            res_y.append(y[i])
        return res_x, res_y

    def get_plots(self, x, y):
        res_x = []
        res_y = []

        res_x = [self.res_x[0]]
        for i in range(1, len(x)):
            res_x.append(x[i])
            res_x.append(x[i])

        for v in range(0, len(y[0])):
            plot_y = []
            for i in range(len(y)-1):
                plot_y.append(y[i][v])
                plot_y.append(y[i][v])
            plot_y.append(y[-1][v])
            res_y.append(plot_y)

        return res_x, res_y


    def show_plot(self, variable_names=[], forcing_variable_names=[]):

        x_data, all_y_data = self.get_plots(self.res_x, self.res_y)

        if self.have_forced_inputs:
            forced_x_data, all_forced_y_data = self.get_plots(self.forced_x, self.forced_y)
            num_forced_plots = len(all_forced_y_data)
            num_plots = len(all_y_data) + num_forced_plots

            num_plot = 1

            for y_data in all_forced_y_data:
                plt.subplot(num_plots, 1, num_plot)
                plt.plot(forced_x_data, y_data)
                if num_plot <= len(forcing_variable_names):
                    plt.title(forcing_variable_names[num_plot - 1])
                plt.yticks([0, 1])
                plt.grid(True)
                num_plot += 1

        else:
            num_plots = len(all_y_data)
            num_forced_plots = 0
            num_plot = 1

        for y_data in all_y_data:
            plt.subplot(num_plots, 1, num_plot)
            plt.plot(x_data, y_data)
            if num_plot - num_forced_plots <= len(variable_names):
                plt.title(variable_names[num_plot - num_forced_plots - 1])
            if num_plot == num_plots:
                plt.xlabel('time')
            plt.yticks([0, 1])
            plt.grid(True)

            num_plot += 1

        plt.tight_layout()
        plt.show()
