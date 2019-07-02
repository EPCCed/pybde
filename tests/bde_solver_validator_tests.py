import unittest
from pybde import BooleanTimeSeries, BDESolver
from pybde import bde_solver_validator

class TestBDESolverValidator(unittest.TestCase):

    def test_one_variable(self):

        history = BooleanTimeSeries([0], [False], 1)

        solver = BDESolver(lambda z : [not z[0][0]], [1], [history])
        result = solver.solve(3)

        validator = bde_solver_validator.BDESolverValidator(lambda z : [not z[0][0]], [1], result)

        self.assertEqual(0, validator.validate(1, 3))


    def test_two_variable(self):

        tau1 = 1
        tau2 = 0.5
        delays = [tau1, tau2]

        history_a = BooleanTimeSeries([0, 1.5], [True, False], 1.8)
        history_b = BooleanTimeSeries([0, 0.5], [True, False], 1.8)

        x_end = 5.2

        solver = BDESolver(lambda z:[z[0][1], not z[1][0]], delays, [history_a, history_b])
        result = solver.solve(x_end)

        validator = bde_solver_validator.BDESolverValidator(
            lambda z:[z[0][1], not z[1][0]], delays, result)

        self.assertEqual(0, validator.validate(1.8, x_end))

    def test_long_two_variable(self):

        tau1 = 1
        tau2 = 0.5
        delays = [tau1, tau2]

        history_a = BooleanTimeSeries([0, 1.5], [True, False], 1.8)
        history_b = BooleanTimeSeries([0, 0.5], [True, False], 1.8)

        x_end = 200

        solver = BDESolver(lambda z:[z[0][1], not z[1][0]], delays, [history_a, history_b])
        result = solver.solve(x_end)

        validator = bde_solver_validator.BDESolverValidator(
            lambda z:[z[0][1], not z[1][0]], delays, result)

        self.assertEqual(0, validator.validate(1.8, x_end))

    def test_forcing_input(self):

        tau1 = 0.5
        delays = [tau1]

        history = BooleanTimeSeries([0, 0.5, 1.5], [True, False, True], 1.7)
        x_end = 3

        input = BooleanTimeSeries([0, 0.5, 1.5, 2, 2.5, 3], [False, True, False, True, False, True], 3)

        solver = BDESolver(lambda z, z2 :[ z2[0][0] ], delays, [history], [input])
        result = solver.solve(x_end)

        validator = bde_solver_validator.BDESolverValidator(lambda z, z2 :[ z2[0][0] ], delays, result, [input])

        self.assertEqual(0, validator.validate(1.7, x_end))


