import unittest
from pybde import SwitchPoints


class TestSwitchPoints(unittest.TestCase):

    def test_basic_merge(self):
        in1 = SwitchPoints([0, 1, 2, 3], [True, False, True, False], 4)
        in2 = SwitchPoints([0, 1, 2.5, 3], [True, False, True, False], 4)

        expected_t = [0, 1, 2, 2.5, 3]
        expected_y = [[True, True], [False, False], [True, False], [True, True], [False, False]]

        res_t, res_y = SwitchPoints.merge([in1, in2])

        self.assertEqual(expected_t, res_t)
        self.assertEqual(expected_y, res_y)


    def test_basic_unmerge(self):

        in1 = SwitchPoints([0, 1, 2, 3], [True, False, True, False], 4)
        in2 = SwitchPoints([0, 1, 2.5, 3], [True, False, True, False], 4)

        t = [0, 1, 2, 2.5, 3]
        y = [[True, True], [False, False], [True, False], [True, True], [False, False]]

        print("Ouptut of unmerge = {}".format(SwitchPoints.unmerge(t, y, 4)))
        [out1, out2] = SwitchPoints.unmerge(t, y, 4)

        self.assertEqual([0, 1, 2, 3], out1.t)
        self.assertEqual([True, False, True, False], out1.y)
        self.assertEqual(4, out1.end)

        self.assertEqual([0, 1, 2.5, 3], out2.t)
        self.assertEqual([True, False, True, False], out2.y)
        self.assertEqual(4, out2.end)
