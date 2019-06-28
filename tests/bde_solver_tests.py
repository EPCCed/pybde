import unittest
from pybde import BDESolver
from pybde import BooleanTimeSeries

class TestBDESolver(unittest.TestCase):

    def test_raise_exception_if_end_before_start(self):

        solver = BDESolver(lambda z : [not z[0][0]], [1], [BooleanTimeSeries([0], [True], 2)])

        with self.assertRaises(ValueError):
            solver.solve(1.7)

    def test_one_variable(self):

        history = BooleanTimeSeries([0, 1], [False, True], 1.5)
        solver = BDESolver(lambda z : [not z[0][0]], [1], [history])
        [output] = solver.solve(3)

        expected_t = [0, 1, 2, 3]
        expected_y = [False, True, False, True]

        self.assertEqual(expected_t, output.t)
        self.assertEqual(expected_y, output.y)
        self.assertEqual(3, output.end)

    def test_one_variable_one_history_switch(self):

        history = BooleanTimeSeries([0], [False], 1)

        solver = BDESolver(lambda z : [not z[0][0]], [1], [history])
        [output] = solver.solve(3)

        expected_t = [0,1,2,3]
        expected_y = [False, True, False, True]

        self.assertEqual(expected_t, output.t)
        self.assertEqual(expected_y, output.y)
        self.assertEqual(3, output.end)

    def test_start_time_is_a_switch_but_not_candidate_from_history(self):

        history = BooleanTimeSeries([0], [False], 1.5)

        solver = BDESolver(lambda z : [not z[0][0]], [1], [history])
        [output] = solver.solve(3)

        expected_t = [0,1.5,2.5]
        expected_y = [False, True, False]

        self.assertEqual(expected_t, output.t)
        self.assertEqual(expected_y, output.y)
        self.assertEqual(3, output.end)

    def test_rounding_issues(self):
        """
        This example got the wrong results due to rounding errors in initial implementation.
        Explicitly keeping track what indexes are associated with candidate switch points
        sorts this problem.  But is it a useful regression test.
        """

        delay_parameters = [0.3]
        start_time = 0.5
        end_time = 3

        history = BooleanTimeSeries([0], [True], start_time)
        input = BooleanTimeSeries([0, 0.5, 1, 1.5, 2, 2.5, 3], [False], end_time)

        my_bde_solver = BDESolver(lambda z,z2 : [z2[0][0]], delay_parameters, [history], [input])
        [output] = my_bde_solver.solve(end_time)

        expected_t = [0, 0.5, 0.8, 1.3, 1.8, 2.3, 2.8]
        expected_y = [True, False, True, False, True, False,True]

        self.assertEqual(expected_t, output.t)
        self.assertEqual(expected_y, output.y)
        self.assertEqual(end_time, output.end)

    def test_two_variables(self):

        # A simple test: 2 variables, 2 delays.
        # x1(t) = x2(t - tau1)
        # x2(t) = NOT x1(t-tau2)

        tau1 = 1
        tau2 = 0.5
        delays = [tau1, tau2]

        history_a = BooleanTimeSeries([0, 1.5], [True, False], 1.8)
        history_b = BooleanTimeSeries([0, 0.5], [True, False], 1.8)

        x_end = 5.2

        solver = BDESolver(lambda z:[z[0][1], not z[1][0]], delays, [history_a, history_b])
        [output_a, output_b] = solver.solve(x_end)

        self.assertEqual([0, 1.5, 3, 4.5], output_a.t)
        self.assertEqual([True, False, True, False], output_a.y)
        self.assertEqual(5.2, output_a.end)

        self.assertEqual([0, 0.5, 2, 3.5, 5], output_b.t)
        self.assertEqual([True, False, True, False, True], output_b.y)
        self.assertEqual(5.2, output_b.end)

    def test_history_ends_with_switch(self):
        # A switch occurs at the last point in the history but the history
        # is consistent with this

        # A simple test: 2 variables, 2 delays.
        # x1(t) = x2(t - tau1)
        # x2(t) = NOT x1(t-tau2)

        tau1 = 1
        tau2 = 0.5
        delays = [tau1, tau2]

        history_a = BooleanTimeSeries([0, 1.5], [True, False], 2.1)
        history_b = BooleanTimeSeries([0, 0.5, 2], [True, False, True], 2.1)

        x_end = 5.2

        solver = BDESolver(lambda z :[ z[0][1], not z[1][0] ], delays, [history_a, history_b])
        [output_a, output_b] = solver.solve(x_end)

        self.assertEqual([0, 1.5, 3, 4.5], output_a.t)
        self.assertEqual([True, False, True, False], output_a.y)
        self.assertEqual(5.2, output_a.end)

        self.assertEqual([0, 0.5, 2, 3.5, 5], output_b.t)
        self.assertEqual([True, False, True, False, True], output_b.y)
        self.assertEqual(5.2, output_b.end)

    def test_error_when_history_inputs_end_at_different_times(self):
        tau1 = 1
        tau2 = 0.5
        delays = [tau1, tau2]

        history_a = BooleanTimeSeries([0, 1.5], [True, False], 2.2)
        history_b = BooleanTimeSeries([0, 0.5, 2], [True, False, True], 2.1)

        x_end = 5.2

        with self.assertRaises(ValueError):
            BDESolver(lambda z :[ z[0][1], not z[1][0] ], delays, [history_a, history_b])

    def test_last_output_is_a_switch_point(self):
        # Same as test_two_variables except the end point has been moved to be on a switch point
        # A simple test: 2 variables, 2 delays.
        # x1(t) = x2(t - tau1)
        # x2(t) = NOT x1(t-tau2)

        tau1 = 1
        tau2 = 0.5
        delays = [tau1, tau2]

        history_a = BooleanTimeSeries([0, 1.5], [True, False], 1.8)
        history_b = BooleanTimeSeries([0, 0.5], [True, False], 1.8)

        x_end = 5

        solver = BDESolver(lambda z :[ z[0][1], not z[1][0] ], delays, [history_a, history_b])
        [output_a, output_b] = solver.solve(x_end)

        self.assertEqual([0, 1.5, 3, 4.5], output_a.t)
        self.assertEqual([True, False, True, False], output_a.y)
        self.assertEqual(5, output_a.end)

        self.assertEqual([0, 0.5, 2, 3.5, 5], output_b.t)
        self.assertEqual([True, False, True, False, True], output_b.y)
        self.assertEqual(x_end, output_b.end)

    def test_two_variables_switch_at_switch_points(self):
        # Two variables switch at each of the switch points.

        # x1(t) = x2(t - tau1)
        # x2(t) = x1(t - tau2)

        tau1 = 1;
        tau2 = 1;
        delays = [tau1, tau2]

        history_a = BooleanTimeSeries([0, 0.5, 1.0, 1.5], [True, False, True, False], 1.8)
        history_b = BooleanTimeSeries([0, 0.5, 1.0, 1.5], [True, False, True, False], 1.8)

        x_end = 3.2

        solver = BDESolver(lambda z :[ z[0][1], z[1][0] ], delays, [history_a, history_b])
        [output_a, output_b] = solver.solve(x_end)

        self.assertEqual([0, 0.5, 1.0, 1.5, 2, 2.5, 3], output_a.t)
        self.assertEqual([True, False, True, False, True, False, True], output_a.y)
        self.assertEqual(3.2, output_a.end)

        self.assertEqual([0, 0.5, 1.0, 1.5, 2, 2.5, 3], output_b.t)
        self.assertEqual([True, False, True, False, True, False, True], output_b.y)
        self.assertEqual(x_end, output_b.end)


    def test_forcing_input(self):

        # A test case with some forcing input.

        # x1(t) = 1 if t mod 1 > 0.5, 0 otherwise   <- this is the forced input
        # x2(t) = x1(t-tau1)                        <- this is the output

        tau1 = 0.5
        delays = [tau1]

        history = BooleanTimeSeries([0, 0.5, 1.5], [True, False, True], 1.7)
        x_end = 3

        input = BooleanTimeSeries([0, 0.5, 1.5, 2, 2.5, 3], [False, True, False, True, False, True], 3)

        solver = BDESolver(lambda z,z2 :[ z2[0][0] ], delays, [history], [input])
        [output] = solver.solve(x_end)

        self.assertEqual([0, 0.5, 1.5, 2, 2.5, 3 ], output.t)
        self.assertEqual([True, False, True, False, True, False], output.y)
        self.assertEqual(x_end, output.end, )

    def test_forcing_input_2(self):
        # A test case with 2 variables and one forcing input.
        # This is equivalent to the 1 loop Neurospora model.
        # This is also a useful test because all of the delays are the
        # same, hence we must deal with multiple candidate switches at
        # each point.
        #
        # This test contains a switch that is the result of a model
        # variable that originates from a forcing switch.

        delays = [1, 1, 1]

        # NOTE: In the original Matlab test this used the line below, but the second point is inconsistent with the
        # model is changed for the output.  We do not yet support this functionality so change it just now.
        #x = [0, 1]
        #y = [[True, False], [True, False]]

        history_a = BooleanTimeSeries([0], [True], 1)
        history_b = BooleanTimeSeries([0], [False], 1)

        x_end = 5

        input = BooleanTimeSeries([0, 0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75, 4.25, 4.75],
                                  [False, True, False, True, False, True, False, True, False, True, False], 5)

        solver = BDESolver(
            lambda z, z2: [z[0][1], (not z[1][0]) or z2[2][0] ],
            delays, [history_a, history_b], [input])

        [output_a, output_b] = solver.solve(x_end)

        self.assertEqual([0, 1, 2.25, 2.75, 3, 5], output_a.t)
        self.assertEqual([True, False, True, False, True, False], output_a.y)
        self.assertEqual(5, output_a.end)

        self.assertEqual([0, 1.25, 1.75, 2, 4, 4.25, 4.75], output_b.t)
        self.assertEqual([False, True, False, True, False, True, False], output_b.y)
        self.assertEqual(5, output_b.end)


    def test_forcing_input2_2on(self):

        # A test case with 2 variables and 2 forcing inputs (second
        # forcing variable is always on which makes the output
        # equivalent to forcing_input_2)

        delays = [1, 1, 1, 1]

        # NOTE: In the original Matlab test this used the line below, but the second point is
        # inconsistent with the model is changed for the output.  We do not yet support this
        # functionality so change it just now.
        #x = [0, 1]
        #y = [[True, False], [True, False]]
        history_a = BooleanTimeSeries([0], [True], 1)
        history_b = BooleanTimeSeries([0], [False], 1)

        x_end = 5

        input_a = BooleanTimeSeries([0, 0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75, 4.25, 4.75], [False], 5)
        input_b = BooleanTimeSeries([0], [True], 5)

        solver = BDESolver(lambda z, z2: [z[0][1] and z2[3][1], (not z[1][0]) or z2[2][0] ],
                           delays, [history_a, history_b], [input_a, input_b])

        [output_a, output_b]= solver.solve(x_end)

        self.assertEqual([0, 1, 2.25, 2.75, 3, 5], output_a.t)
        self.assertEqual([True, False, True, False, True, False], output_a.y)
        self.assertEqual(5, output_a.end)

        self.assertEqual([0, 1.25, 1.75, 2, 4, 4.25, 4.75], output_b.t)
        self.assertEqual([False, True, False, True, False, True, False], output_b.y)
        self.assertEqual(x_end, output_b.end)

    def test_forcing_input_2_2(self):

        # test case with 2 variables and 2 forcing inputs

        tau1 = 1
        tau2 = 0.5
        tau3 = 1
        tau4 = 0.25

        delays = [tau1, tau2, tau3, tau4]

        history_a = BooleanTimeSeries([0], [True], 1)
        history_b = BooleanTimeSeries([0], [False], 1)

        x_end = 1.4

        input_a = BooleanTimeSeries([0, 0.25, 0.75, 1.25], [False], 1.4)
        input_b = BooleanTimeSeries([0, 0.1, 0.9, 1.1], [False], 1.4)

        solver = BDESolver(
            lambda z, z2: [z[0][1] or not z2[3][1], (not z[1][0]) or z2[2][0] ],
            delays, [history_a, history_b], [input_a, input_b])

        [output_a, output_b] = solver.solve(x_end)

        self.assertEqual([0, 1, 1.15, 1.35], output_a.t)
        self.assertEqual([True, False, True, False], output_a.y)
        self.assertEqual(1.4, output_a.end)

        self.assertEqual([0, 1.25], output_b.t)
        self.assertEqual([False, True], output_b.y)
        self.assertEqual(1.4, output_b.end)

    def test_error_when_first_input_switch_point_is_not_zero(self):
        """
        Tests that error is raised when the first input switch point
        is not at time zero.
        """

        tau1 = 1
        tau2 = 0.5
        delays = [tau1, tau2]

        history = BooleanTimeSeries([0.2, 0.5, 1.5], [True], 1.7)

        x_end = 5

        with self.assertRaises(ValueError):
            BDESolver(lambda z :[ z[0][1], not z[1][0] ], delays, [history])

    def test_error_when_first_forced_input_switch_point_is_not_zero(self):
        """
        Tests that error is raised when the first forced input switch point
        is not at time zero.
        """

        tau1 = 1
        tau2 = 0.5
        delays = [tau1, tau2]

        history = BooleanTimeSeries([0.2, 0.5, 1.5], [True], 1.7)

        forced_input = BooleanTimeSeries([1], [True], 1.7)

        x_end = 5

        with self.assertRaises(ValueError):
            BDESolver(lambda z: [z[0][1], not z[1][0]], delays, [history], [forced_input])

    def test_error_when_given_negative_delay(self):
        tau1 = 1
        tau2 = -0.5
        delays = [tau1, tau2]

        history = BooleanTimeSeries([0, 0.5, 1.5], [True], 1.7)

        x_end = 5

        with self.assertRaises(ValueError):
            BDESolver(lambda z: [z[0][1], not z[1][0]], delays, [history])


if __name__ == '__main__':
    unittest.main()
