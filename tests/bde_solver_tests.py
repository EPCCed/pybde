import unittest
from pybde import BDESolver


class TestBDESolver(unittest.TestCase):

    def test_raise_exception_if_end_before_start(self):
        solver = BDESolver(lambda z : [not z[0][0]], [1], [0,1,1.5], [[False],[True],[True]])

        with self.assertRaises(ValueError):
            solver.solve(2, 1.7)

    def test_one_variable(self):
        solver = BDESolver(lambda z : [not z[0][0]], [1], [0,1,1.5], [[False],[True],[True]])
        solver.solve(1.6, 3)

        expected_x = [0,1,1.5,2,3]
        expected_y = [[False],[True],[True],[False],[True]]

        self.assertEqual(expected_x, solver.res_x)
        self.assertEqual(expected_y, solver.res_y)

    def test_single_input_switch(self):
        solver = BDESolver(lambda z : [not z[0][0]], [1], [0], [[False]])
        solver.solve(1,3)

        expected_x = [0,1,2,3]
        expected_y = [[False],[True],[False],[True]]

        self.assertEqual(expected_x, solver.res_x)
        self.assertEqual(expected_y, solver.res_y)

    def test_start_time_is_a_switch_but_not_candidate_from_input(self):
        solver = BDESolver(lambda z : [not z[0][0]], [1], [0], [[False]])
        solver.solve(1.5, 3)

        expected_x = [0,1.5,2.5,3]
        expected_y = [[False],[True],[False],[False]]

        self.assertEqual(expected_x, solver.res_x)
        self.assertEqual(expected_y, solver.res_y)

    def test_rounding_issues(self):
        """
        This example got the wrong results due to rounding errors in initial implementation.
        Explicitly keeping track what indexes are associated with candidate switch points
        sorts this problem.  But is it a useful regression test.
        """

        input_times = [0]
        input_states = [[True]]
        delay_parameters = [0.3]
        start_time = 0.5
        end_time = 3

        forcing_times = [0, 0.5, 1, 1.5, 2, 2.5, 3]
        forcing_states = [[False], [True], [False], [True], [False], [True], [False]]

        my_bde_solver = BDESolver(lambda z,z2 : [z2[0][0]], delay_parameters, input_times, input_states, forcing_times,
                                  forcing_states)
        my_bde_solver.solve(start_time, end_time)

        expected_x = [0, 0.5, 0.8, 1.3, 1.8, 2.3, 2.8, 3 ]
        expected_y = [[True],[False],[True],[False],[True], [False], [True], [True]]

        self.assertEqual(expected_x, my_bde_solver.res_x)
        self.assertEqual(expected_y, my_bde_solver.res_y)


    def test_two_variables(self):

        # A simple test: 2 variables, 2 delays.
        # x1(t) = x2(t - tau1)
        # x2(t) = NOT x1(t-tau2)

        tau1 = 1
        tau2 = 0.5
        delays = [tau1, tau2]

        x = [0, 0.5, 1.5, 1.7]
        y = BDESolver.to_logical([[1, 1], [1, 0], [0, 0], [0, 0]])

        x_end = 5.2

        solver = BDESolver(lambda z:[z[0][1], not z[1][0]], delays, x, y)
        solver.solve(1.8, x_end)

        expected_x = [0, 0.5, 1.5, 1.7, 2, 3, 3.5, 4.5, 5, 5.2]
        expected_y = BDESolver.to_logical([[1,1],[1,0],[0,0],[0,0],[0,1],[1,1],[1,0],[0,0],[0,1],[0,1]])

        self.assertEqual(expected_x, solver.res_x)
        self.assertEqual(expected_y, solver.res_y)


    def test_history_ends_with_switch(self):
        # A switch occurs at the last point in the history but the history
        # is consistent with this

        # A simple test: 2 variables, 2 delays.
        # x1(t) = x2(t - tau1)
        # x2(t) = NOT x1(t-tau2)

        tau1 = 1
        tau2 = 0.5
        delays  = [tau1, tau2]

        x = [0,0.5,1.5,2]
        y = [[True,True], [True,False], [False,False], [False,True]]

        x_end = 5.2

        solver = BDESolver(lambda z :[ z[0][1], not z[1][0] ], delays, x, y)
        solver.solve(2.1, x_end)

        expected_x = [0,0.5,1.5,2,3,3.5,4.5,5,5.2]
        expected_y = [[True,True], [True,False], [False,False], [False,True], [True,True], [True,False], [False,False], [False,True], [False,True]]

        self.assertEqual(expected_x, solver.res_x)
        self.assertEqual(expected_y, solver.res_y)
        
    def test_simulation_starts_from_last_input_time(self):
        """
        Simulations are not allowed to start from the last input time.
        Tests that condition is flagged as an error.
        """

        tau1 = 1
        tau2 = 0.5
        delays  = [tau1, tau2]

        x = [0,0.5,1.5,1.7]
        y = [[True,True], [True,False], [False,False], [False,False]]

        x_end = 5

        solver = BDESolver(lambda z :[ z[0][1], not z[1][0] ], delays, x, y)

        with self.assertRaises(ValueError):
            solver.solve(1.7, x_end)

    def test_last_output_is_a_switch_point(self):
        # Same as test_two_variables except the end point has been moved to be on a switch point
        # A simple test: 2 variables, 2 delays.
        # x1(t) = x2(t - tau1)
        # x2(t) = NOT x1(t-tau2)

        tau1 = 1
        tau2 = 0.5
        delays  = [tau1, tau2]

        x = [0,0.5,1.5,1.7]
        y = [[True,True], [True,False], [False,False], [False,False]]

        x_end = 5

        solver = BDESolver(lambda z :[ z[0][1], not z[1][0] ], delays, x, y)
        solver.solve(1.8, x_end)

        expected_x = [0,0.5,1.5,1.7,2,3,3.5,4.5,5]
        expected_y = [[True,True], [True,False], [False,False], [False,False], [False,True], [True,True], [True,False], [False,False], [False,True]]

        self.assertEqual(expected_x, solver.res_x)
        self.assertEqual(expected_y, solver.res_y)

    def test_two_variables_switch_at_switch_points(self):
        # Two variables switch at each of the switch points.

        # x1(t) = x2(t - tau1)
        # x2(t) = x1(t - tau2)

        tau1 = 1;
        tau2 = 1;
        delays = [tau1, tau2]
        x = [0, 0.5, 1.0, 1.5, 1.7]
        y = [[True,True], [False,False], [True,True], [False,False], [False,False]]

        x_end = 3.2

        solver = BDESolver(lambda z :[ z[0][1], z[1][0] ], delays, x, y)
        solver.solve(1.8, x_end)

        expected_x = [0, 0.5, 1.0, 1.5, 1.7, 2, 2.5, 3, 3.2]
        expected_y = [[True,True], [False,False], [True,True], [False,False], [False,False], [True,True], [False,False], [True,True], [True,True]]

        self.assertEqual(expected_x, solver.res_x)
        self.assertEqual(expected_y, solver.res_y)

    def test_forcing_input(self):

        # A test case with some forcing input.

        # x1(t) = 1 if t mod 1 > 0.5, 0 otherwise   <- this is the forced input
        # x2(t) = x1(t-tau1)                        <- this is the output

        tau1 = 0.5
        delays = [tau1]

        x = [  0,     0.5,     1.5,   ]
        y = [ [True], [False], [True] ]

        x_end = 3

        forcing_x = [ 0,       0.5,   1.5,     2,      2.5,     3     ]
        forcing_y = [[False], [True], [False], [True], [False], [True]]

        solver = BDESolver(lambda z,z2 :[ z2[0][0] ], delays, x, y, forcing_x, forcing_y)
        solver.solve(1.7, x_end)

        expected_x = [  0,     0.5,     1.5,     2,       2.5,    3       ]
        expected_y = [ [True], [False], [True],  [False], [True], [False] ]

        self.assertEqual(expected_x, solver.res_x)
        self.assertEqual(expected_y, solver.res_y)

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
        x = [0]
        y = [[True, False]]

        x_end = 5

        print("x before: {}".format(x))

        forcing_x = [0, 0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75, 4.25, 4.75, 5]
        forcing_y = [[False], [True], [False], [True], [False], [True], [False], [True], [False], [True], [False], [False]]

        solver = BDESolver(lambda z, z2: [z[0][1], (not z[1][0]) or z2[2][0] ], delays, x, y, forcing_x, forcing_y)

        solver.solve(1, x_end)

        expected_x = [0, 1, 1.25, 1.75, 2, 2.25, 2.75, 3, 4, 4.25, 4.75, 5]
        expected_y = [[True, False],[False,False], [False,True], [False,False], [False,True], [True,True], [False,True], [True,True], [True,False], [True,True], [True,False], [False,False]]

        print("Result x {}\nResult y{}\nExpected x:{}\nExpected y:{}".format(solver.res_x,solver.res_y,expected_x,expected_y))

        print("x after: {}".format(x))

        self.assertEqual(expected_x, solver.res_x)
        self.assertEqual(expected_y, solver.res_y)

    def test_forcing_input2_2on(self):

        # A test case with 2 variables and 2 forcing inputs (second
        # forcing variable is always on which makes the output
        # equivalent to forcing_input_2)

        delays = [1, 1, 1, 1]

        # NOTE: In the original Matlab test this used the line below, but the second point is inconsistent with the
        # model is changed for the output.  We do not yet support this functionality so change it just now.
        #x = [0, 1]
        #y = [[True, False], [True, False]]
        x = [0]
        y = [[True, False]]

        x_end = 5

        forcing_x = [0, 0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75, 4.25, 4.75, 5]
        forcing_y = BDESolver.to_logical([[0,1], [1,1], [0,1], [1,1], [0,1], [1,1], [0,1], [1,1], [0,1], [1,1], [0,1], [0,1]])

        solver = BDESolver(lambda z, z2: [z[0][1] and z2[3][1], (not z[1][0]) or z2[2][0] ], delays, x, y, forcing_x, forcing_y)

        solver.solve(1, x_end)

        expected_x = [0, 1, 1.25, 1.75, 2, 2.25, 2.75, 3, 4, 4.25, 4.75, 5]
        expected_y = BDESolver.to_logical([[1,0], [0,0], [0,1], [0,0], [0,1], [1,1], [0,1], [1,1], [1,0], [1,1], [1,0], [0,0]])

        self.assertEqual(expected_x, solver.res_x)
        self.assertEqual(expected_y, solver.res_y)

    def test_forcing_input_2_2(self):

        # test case with 2 variables and 2 forcing inputs

        tau1 = 1
        tau2 = 0.5
        tau3 = 1
        tau4 = 0.25

        delays = [tau1, tau2, tau3, tau4]

        x = [0]
        y = BDESolver.to_logical([[1, 0]])

        x_end = 1.4

        forcing_x = [0, 0.1, 0.25, 0.75, 0.9, 1.1, 1.25, 1.4]
        forcing_y = BDESolver.to_logical([[0,0], [0,1], [1,1], [0,1], [0,0], [0,1], [1,1], [1,1]])

        solver = BDESolver(
            lambda z, z2: [z[0][1] or not z2[3][1], (not z[1][0]) or z2[2][0] ],
            delays, x, y, forcing_x, forcing_y)

        solver.solve(1, x_end)

        print("************* Result is t = {}, y = {} ".format(solver.res_x, solver.res_y))

        expected_x = [0, 1, 1.15, 1.25, 1.35, 1.4]
        expected_y = BDESolver.to_logical([[1,0], [0,0], [1,0], [1,1], [0,1], [0,1]])


        self.assertEqual(expected_x, solver.res_x)
        self.assertEqual(expected_y, solver.res_y)



if __name__ == '__main__':
    unittest.main()
