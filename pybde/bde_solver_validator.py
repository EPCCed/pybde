import heapq
import random
from pybde import BooleanTimeSeries


class ValidatorCandidateSwitchPoints:
    """
    Class used to produce candidate switch points for the validator.

    Parameters
    ----------

    delays : list of floats
        The delays used by the simulation
    start : float
        Start time of the simulation
    end :
        End time of the simulation
    """
    def __init__(self, delays, start, end):
        self.delays = delays
        self._times = []
        self.start = start
        self.end = end

    def add_delays(self, t):
        """
        Adds the delays to the given time as candidate switch points.

        Parameters
        ----------

        t : float
            Time from which to add delays.
        """
        for delay in self.delays:
            self.add(t+delay)

    def add(self, t):
        """
        Adds a new candidate switch time.

        Parameters
        ----------

        t : float
            Time from which to add.
        """
        if self.start <= t <= self.end:
            heapq.heappush(self._times, t)

    def add_random(self, n_random_times):
        """
        Adds some random candidate switch times.

        Parameters
        ----------

        n_random_times : float
            Number of random times to add.
        """
        for x in range(n_random_times):
            r = random.random()
            heapq.heappush(self._times, r * (self.end-self.start) + self.start)

    def add_boolean_time_series(self, bts):
        """
        Adds all the switch points in the given Boolean time series as candidate switch points.

        Parameters
        ----------

        bts : BooleanTimeSeries
            Boolean time series.
        """
        for t in bts.t:
            self.add(t)
        self.add(bts.end)

    def times(self):
        """
        Iterator to return the candidate switch times in order.
        """
        while self._times:
            yield heapq.heappop(self._times)


class BDESolverValidator:
    """
    Class used to validate the Boolean Delay Equation simulations by testing the output matches
    the equations at many candidate switch points and also at some random candidate switch
    points inside the range of the simulation.

    Parameters
    ----------

    func : function func(Z) or func(Z1,Z2) if forced inputs are used
        Z is a list of lists - first index is delay, second is variable
        so Z[0][2] is the values of the 3rd variable at the 1st delay.
        If forcing inputs are used then a second argument Z2 is passed.
        The indexes are the same except they refer to the forcing inputs.

    delays : list of float
        Values of the time delays.
    variables : list of BooleanTimeSeries
        The output of BDE simulation.
    forcing_inputs: list of BooleanTimeSeries
        Time series for each forcing input. Default value is None.
    """
    def __init__(self, func, delays, variables, forcing_inputs=None):
        self.func = func
        self.delays = delays
        self.variables_bts = variables
        self.inputs = forcing_inputs

    def validate(self, start, end):
        """
        Validates the outputs of the simulation satisfy the model equations.

        Parameters
        ----------

        start : float
            start time of the simulation (i.e. the list time point of the history)

        end : float
            end time of the simulation

        Returns
        -------

        Sum of the the period of time each variable is in an invalid state. The maximum value
        is the length of the simulation multiplied by the number of variables.  The minimum
        value is 0.
        """

        candidate_switch_points = ValidatorCandidateSwitchPoints(self.delays, start, end)

        for bts in self.variables_bts:
            candidate_switch_points.add_boolean_time_series(bts)
        if self.inputs:
            for bts in self.inputs:
                candidate_switch_points.add_boolean_time_series(bts)

        candidate_switch_points.add_random(1000)
        candidate_switch_points.add(start)

        res_times = []
        res_variables_states = []

        for t in candidate_switch_points.times():
            z = []
            z2 = []
            for d in self.delays:
                states = []
                for v_bts in self.variables_bts:
                    states.append(v_bts.get_state(t-d))
                z.append(states)

                if self.inputs:
                    z2_states = []
                    for input_bts in self.inputs:
                        z2_states.append(input_bts.get_state(t-d))
                    z2.append(z2_states)

            if self.inputs:
                s = self.func(z, z2)
            else:
                s = self.func(z)

            if (not res_times) or res_variables_states[-1] != s:
                res_times.append(t)
                res_variables_states.append(s)
                candidate_switch_points.add_delays(t)

        # Turn into Boolean Time Series
        res_variables_bts = BooleanTimeSeries.unmerge(res_times, res_variables_states, end)

        # Calculate the accuracy
        accuracy = 0
        for v_i, res_var_bts in enumerate(res_variables_bts):
            bts_from_start = self.variables_bts[v_i].cut(start, end)
            accuracy += res_var_bts.hamming_distance(bts_from_start)

        return accuracy
