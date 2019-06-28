import unittest
from pybde import BooleanTimeSeries
import numpy as np

class TestBooleanTimeSeries(unittest.TestCase):

    def test_error_if_times_not_incrementing(self):
        with self.assertRaises(ValueError):
            BooleanTimeSeries([0, 1, 4, 2], [True], 10)

    def test_error_if_end_is_before_final_switch_point(self):
        with self.assertRaises(ValueError):
            BooleanTimeSeries([0, 1, 4, 2], [True], 3)

    def test_error_if_more_states_than_switch_points(self):
        with self.assertRaises(ValueError):
            BooleanTimeSeries([0, 1, 4, 2], [True, False, True, False, True], 10)

    def test_pad_out_states(self):
        sp = BooleanTimeSeries([0, 1, 2, 3], [True], 10)
        self.assertEqual([True, False, True, False], sp.y)

    def test_basic_cut(self):
        sp = BooleanTimeSeries([0, 1, 4], [True], 10)
        sp = sp.cut(0, 3)
        self.assertEqual([0, 1], sp.t)
        self.assertEqual([True, False], sp.y)
        self.assertEqual(3, sp.end)

    def test_cut_non_zero_start(self):
        sp = BooleanTimeSeries([0, 1, 2, 4], [True], 10)
        sp = sp.cut(1.5, 3)
        self.assertEqual([1.5, 2], sp.t)
        self.assertEqual([False, True], sp.y)
        self.assertEqual(3, sp.end)

    def test_cut_non_zero_start_on_switch_point(self):
        sp = BooleanTimeSeries([0, 1, 2, 4], [True], 10)
        sp = sp.cut(1, 3)
        self.assertEqual([1, 2], sp.t)
        self.assertEqual([False, True], sp.y)
        self.assertEqual(3, sp.end)

    def test_cut_non_zero_start_after_final_switch(self):
        sp = BooleanTimeSeries([0, 1, 2, 4], [True], 10)
        sp = sp.cut(5,6)
        self.assertEqual([5], sp.t)
        self.assertEqual([False], sp.y)
        self.assertEqual(6, sp.end)

    def test_cut_on_switch_point(self):
        sp = BooleanTimeSeries([0, 1, 4], [True], 10)
        sp = sp.cut(0, 4)
        self.assertEqual([0, 1], sp.t)
        self.assertEqual([True, False], sp.y)
        self.assertEqual(4, sp.end)

    def test_keep_cut_on_switch_point(self):
        sp = BooleanTimeSeries([0, 1, 4], [True], 10)
        sp = sp.cut(0, 4, keep_switch_on_end=True)
        self.assertEqual([0, 1, 4], sp.t)
        self.assertEqual([True, False, True], sp.y)
        self.assertEqual(4, sp.end)

    def test_cut_non_inclusive_start(self):
        sp = BooleanTimeSeries([1, 4], [True], 10)
        with self.assertRaises(ValueError):
            sp.cut(0,3)

    def test_cut_non_inclusive_end(self):
        sp = BooleanTimeSeries([0, 4], [True], 10)
        with self.assertRaises(ValueError):
            sp.cut(0,20)

    def test_cut_end_before_start(self):
        sp = BooleanTimeSeries([0, 4], [True], 10)
        with self.assertRaises(ValueError):
            sp.cut(4,2)

    def test_cut_remove_switch_point_on_end(self):
        bts = BooleanTimeSeries([0, 1, 2], [True], 2)

        cut1 = bts.cut(0, 2)
        self.assertEqual([0,1], cut1.t)
        self.assertEqual([True, False], cut1.y)
        self.assertEqual(2, cut1.end)

    def test_cut_with_no_impact(self):
        bts = BooleanTimeSeries([0, 1], [True], 2)

        cut1 = bts.cut(0, 2)
        self.assertEqual([0,1], cut1.t)
        self.assertEqual([True, False], cut1.y)
        self.assertEqual(2, cut1.end)

    def test_compress(self):
        sp = BooleanTimeSeries([0, 1, 2, 3, 4], [True, False, False, True, False], 10)
        sp = sp.compress()
        self.assertEqual([0, 1, 3, 4], sp.t)
        self.assertEqual([True, False, True, False], sp.y)
        self.assertEqual(10, sp.end)

    def test_basic_merge(self):
        in1 = BooleanTimeSeries([0, 1, 2, 3], [True, False, True, False], 4)
        in2 = BooleanTimeSeries([0, 1, 2.5, 3], [True, False, True, False], 4)

        expected_t = [0, 1, 2, 2.5, 3]
        expected_y = [[True, True], [False, False], [True, False], [True, True], [False, False]]

        res_t, res_y = BooleanTimeSeries.merge([in1, in2])

        self.assertEqual(expected_t, res_t)
        self.assertEqual(expected_y, res_y)

    def test_basic_unmerge(self):

        in1 = BooleanTimeSeries([0, 1, 2, 3], [True, False, True, False], 4)
        in2 = BooleanTimeSeries([0, 1, 2.5, 3], [True, False, True, False], 4)

        t = [0, 1, 2, 2.5, 3]
        y = [[True, True], [False, False], [True, False], [True, True], [False, False]]

        print("Ouptut of unmerge = {}".format(BooleanTimeSeries.unmerge(t, y, 4)))
        [out1, out2] = BooleanTimeSeries.unmerge(t, y, 4)

        self.assertEqual([0, 1, 2, 3], out1.t)
        self.assertEqual([True, False, True, False], out1.y)
        self.assertEqual(4, out1.end)

        self.assertEqual([0, 1, 2.5, 3], out2.t)
        self.assertEqual([True, False, True, False], out2.y)
        self.assertEqual(4, out2.end)

    def test_hamming_distance_to_self_is_zero(self):
        sp = BooleanTimeSeries([0, 1, 2, 3], [True, False, True, False], 4)
        self.assertEqual(0, sp.hamming_distance(sp))

    def test_hamming_distance(self):
        sp1 = BooleanTimeSeries([0, 1, 2, 3], [True, False, True, False], 4)
        sp2 = BooleanTimeSeries([0, 1.5, 2, 3.5], [True, False, True, False], 4)

        self.assertEqual(1, sp1.hamming_distance(sp2))
        self.assertEqual(1, sp2.hamming_distance(sp1))

    def test_hamming_distance_total_mismatch(self):
        sp1 = BooleanTimeSeries([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [True], 11)
        sp2 = BooleanTimeSeries([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [False], 11)

        self.assertEqual(11, sp1.hamming_distance(sp2))
        self.assertEqual(11, sp2.hamming_distance(sp1))

    def test_hamming_distance_differ_at_endpoint(self):
        sp1 = BooleanTimeSeries([0, 1, 2, 3], [True], 4)
        sp2 = BooleanTimeSeries([0, 1, 2, 3, 4], [True], 4)

        self.assertEqual(0, sp1.hamming_distance(sp2))
        self.assertEqual(0, sp2.hamming_distance(sp1))

    def test_hamming_distance_error_if_ranges_differ(self):
        sp1 = BooleanTimeSeries([0, 1, 2, 3], [True], 10)
        sp2 = BooleanTimeSeries([0, 1, 2, 3, 4], [True], 4)

        with self.assertRaises(ValueError):
            sp1.hamming_distance(sp2)

    def test_absolute_threshold(self):
        x = [0, 1, 2]
        y = [0, 10, 0]
        sp = BooleanTimeSeries.absolute_threshold(x, y, 5)
        self.assertEqual([0, 0.5, 1.5], sp.t)
        self.assertEqual([False, True, False], sp.y)
        self.assertEqual(2, sp.end)

    def test_absolute_threshold_touch_threshold_from_below(self):
        x = [0, 1, 2]
        y = [0, 5, 0]
        sp = BooleanTimeSeries.absolute_threshold(x, y, 5)
        self.assertEqual([0], sp.t)
        self.assertEqual([False], sp.y)
        self.assertEqual(2, sp.end)

    def test_absolute_threshold_touch_threshold_from_above(self):
        x = [0, 1, 2]
        y = [10, 5, 10]
        sp = BooleanTimeSeries.absolute_threshold(x, y, 5)
        self.assertEqual([0], sp.t)
        self.assertEqual([True], sp.y)
        self.assertEqual(2, sp.end)

    def test_absolute_threshold_switch_on_single_plateau(self):
        x = [0, 1, 2]
        y = [10, 5, 0]
        sp = BooleanTimeSeries.absolute_threshold(x, y, 5)
        self.assertEqual([0, 1], sp.t)
        self.assertEqual([True, False], sp.y)
        self.assertEqual(2, sp.end)

    def test_absolute_threshold_switch_on_multiple_plateau(self):
        x = [0, 1, 2, 3, 4]
        y = [10, 5, 5, 0, 1]
        sp = BooleanTimeSeries.absolute_threshold(x, y, 5)
        self.assertEqual([0, 1.5], sp.t)
        self.assertEqual([True, False], sp.y)
        self.assertEqual(4, sp.end)

    def test_absolute_threshold_start_with_plateau(self):
        x = [0, 1,   2, 3,  4]
        y = [5, 10, 10, 0, 10]
        sp = BooleanTimeSeries.absolute_threshold(x, y, 5)
        self.assertEqual([0, 2.5, 3.5], sp.t)
        self.assertEqual([True, False, True], sp.y)
        self.assertEqual(4, sp.end)

    def test_absolute_threshold_start_with_double_plateau(self):
        x = [0, 1,  2, 3,  4]
        y = [5, 5,  0, 10, 0]
        sp = BooleanTimeSeries.absolute_threshold(x, y, 5)
        self.assertEqual([0, 2.5, 3.5], sp.t)
        self.assertEqual([False, True, False], sp.y)
        self.assertEqual(4, sp.end)

    def test_absolute_threshold_all_on_plateau(self):
        t = [0, 1, 2, 3]
        y = [5, 5, 5, 5]
        sp = BooleanTimeSeries.absolute_threshold(t, y, 5)
        self.assertEqual([0], sp.t)
        self.assertEqual([False], sp.y)
        self.assertEqual(3, sp.end)


    def test_absolute_threshold_switch_on_threshold(self):
        x = [0, 1, 2]
        y = [10, 5, 0]
        sp = BooleanTimeSeries.absolute_threshold(x, y, 5)
        self.assertEqual([0, 1], sp.t)
        self.assertEqual([True, False], sp.y)
        self.assertEqual(2, sp.end)

    def test_relative_threshold(self):
        x = [0, 1, 2]
        y = [10, 20, 10]
        sp = BooleanTimeSeries.relative_threshold(x, y, 0.5)
        self.assertEqual([0, 0.5, 1.5], sp.t)
        self.assertEqual([False, True, False], sp.y)
        self.assertEqual(2, sp.end)

    def test_create_with_numpy_arrays(self):
        t = np.array([0, 1, 2])
        y = np.array([False, True, False])

        bts = BooleanTimeSeries(t, y, 3)

        self.assertEqual([0, 1, 2], bts.t)
        self.assertEqual([False, True, False], bts.y)
        self.assertEqual(3, bts.end)


