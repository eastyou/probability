"""概率模型单元测试。"""

import math
import unittest

from probability.model import (
    bag_probability,
    check_answer,
    coin_probability,
    dice_sum_distribution,
    dice_sum_probability,
    die_probability,
    expected_value,
    format_probability,
    make_quiz,
    spinner_probability,
    validate_probability,
)


class ValidateProbabilityTests(unittest.TestCase):
    def test_accepts_boundaries(self) -> None:
        self.assertEqual(validate_probability(0), 0.0)
        self.assertEqual(validate_probability(0.0), 0.0)
        self.assertEqual(validate_probability(1), 1.0)
        self.assertEqual(validate_probability(1.0), 1.0)

    def test_accepts_typical_values(self) -> None:
        for value in (0.5, 0.25, 1.0 / 3.0, 0.999999):
            with self.subTest(value=value):
                self.assertAlmostEqual(validate_probability(value), value)

    def test_returns_float(self) -> None:
        self.assertIsInstance(validate_probability(1), float)

    def test_rejects_bool(self) -> None:
        for value in (True, False):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_probability(value)

    def test_rejects_non_numeric(self) -> None:
        for value in ("0.5", None, [], object()):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_probability(value)

    def test_rejects_nan(self) -> None:
        with self.assertRaises(ValueError):
            validate_probability(float("nan"))

    def test_rejects_infinity(self) -> None:
        for value in (float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_probability(value)

    def test_rejects_out_of_range(self) -> None:
        for value in (-0.001, -1.0, 1.001, 2):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_probability(value)


class FormatProbabilityTests(unittest.TestCase):
    def test_zero(self) -> None:
        self.assertEqual(format_probability(0), "0（0%）")

    def test_one(self) -> None:
        self.assertEqual(format_probability(1), "1（100%）")

    def test_quarter(self) -> None:
        self.assertEqual(format_probability(0.25), "1/4（25%）")

    def test_half(self) -> None:
        self.assertEqual(format_probability(0.5), "1/2（50%）")

    def test_third(self) -> None:
        self.assertEqual(format_probability(1.0 / 3.0), "1/3（33.33%）")

    def test_decimal_that_simplifies(self) -> None:
        self.assertEqual(format_probability(0.1), "1/10（10%）")
        self.assertEqual(format_probability(5.0 / 36.0), "5/36（13.89%）")

    def test_tolerates_tiny_float_error(self) -> None:
        self.assertEqual(format_probability(0.25 + 1e-12), "1/4（25%）")

    def test_falls_back_to_decimal(self) -> None:
        self.assertEqual(format_probability(0.123456789), "0.1235（12.35%）")

    def test_rejects_invalid_probability(self) -> None:
        for value in (1.5, -0.1, float("nan")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    format_probability(value)


class CoinProbabilityTests(unittest.TestCase):
    def test_chinese_faces(self) -> None:
        self.assertEqual(coin_probability("正面"), 0.5)
        self.assertEqual(coin_probability("反面"), 0.5)

    def test_english_faces_are_case_insensitive(self) -> None:
        self.assertEqual(coin_probability("heads"), 0.5)
        self.assertEqual(coin_probability("Heads"), 0.5)
        self.assertEqual(coin_probability(" TAILS "), 0.5)

    def test_invalid_face(self) -> None:
        for value in ("", "硬币", "head", "正面朝上"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    coin_probability(value)

    def test_non_string_face(self) -> None:
        for value in (1, None, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    coin_probability(value)


class DieProbabilityTests(unittest.TestCase):
    def test_even_and_odd(self) -> None:
        self.assertAlmostEqual(die_probability("偶数"), 0.5)
        self.assertAlmostEqual(die_probability("奇数"), 0.5)

    def test_inequalities(self) -> None:
        self.assertAlmostEqual(die_probability("大于4"), 1.0 / 3.0)
        self.assertAlmostEqual(die_probability("小于3"), 1.0 / 3.0)
        self.assertAlmostEqual(die_probability("大于 4"), 1.0 / 3.0)

    def test_specific_faces(self) -> None:
        for face in ("1", "2", "3", "4", "5", "6"):
            with self.subTest(face=face):
                self.assertAlmostEqual(die_probability(face), 1.0 / 6.0)

    def test_invalid_conditions(self) -> None:
        for value in ("", "0", "7", "等于3", "2.0", "大于7"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    die_probability(value)

    def test_non_string_condition(self) -> None:
        with self.assertRaises(ValueError):
            die_probability(3)

    def test_result_within_unit_interval(self) -> None:
        probability = die_probability("偶数")
        self.assertGreaterEqual(probability, 0.0)
        self.assertLessEqual(probability, 1.0)


class DiceSumProbabilityTests(unittest.TestCase):
    def test_extremes(self) -> None:
        self.assertAlmostEqual(dice_sum_probability(2), 1.0 / 36.0)
        self.assertAlmostEqual(dice_sum_probability(12), 1.0 / 36.0)

    def test_seven_is_most_likely(self) -> None:
        self.assertAlmostEqual(dice_sum_probability(7), 1.0 / 6.0)

    def test_symmetry(self) -> None:
        for low, high in ((3, 11), (4, 10), (5, 9), (6, 8)):
            with self.subTest(low=low, high=high):
                self.assertAlmostEqual(
                    dice_sum_probability(low), dice_sum_probability(high)
                )

    def test_out_of_range(self) -> None:
        for value in (1, 0, 13, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    dice_sum_probability(value)

    def test_rejects_bool_and_float(self) -> None:
        for value in (True, 7.0):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    dice_sum_probability(value)

    def test_distribution_keys(self) -> None:
        self.assertEqual(sorted(dice_sum_distribution()), list(range(2, 13)))

    def test_distribution_sums_to_one(self) -> None:
        self.assertAlmostEqual(sum(dice_sum_distribution().values()), 1.0, places=12)

    def test_distribution_matches_probability_function(self) -> None:
        for total, probability in dice_sum_distribution().items():
            with self.subTest(total=total):
                self.assertAlmostEqual(probability, dice_sum_probability(total))


class BagProbabilityTests(unittest.TestCase):
    def test_basic_draw(self) -> None:
        self.assertAlmostEqual(bag_probability({"红": 3, "蓝": 1}, "红"), 0.75)
        self.assertAlmostEqual(bag_probability({"红": 3, "蓝": 1}, "蓝"), 0.25)

    def test_target_is_stripped(self) -> None:
        self.assertAlmostEqual(bag_probability({"红": 2, "蓝": 2}, " 红 "), 0.5)

    def test_probabilities_sum_to_one(self) -> None:
        colors = {"红": 1, "蓝": 2, "绿": 3}
        total = sum(bag_probability(colors, color) for color in colors)
        self.assertAlmostEqual(total, 1.0)

    def test_empty_bag(self) -> None:
        with self.assertRaises(ValueError):
            bag_probability({}, "红")

    def test_invalid_counts(self) -> None:
        for colors in ({"红": 0}, {"红": -1}, {"红": True}, {"红": 1.5}, {"红": "3"}):
            with self.subTest(colors=colors):
                with self.assertRaises(ValueError):
                    bag_probability(colors, "红")

    def test_invalid_color_name(self) -> None:
        with self.assertRaises(ValueError):
            bag_probability({"": 1}, "")

    def test_missing_target(self) -> None:
        with self.assertRaises(ValueError):
            bag_probability({"红": 3}, "蓝")

    def test_invalid_target_type(self) -> None:
        with self.assertRaises(ValueError):
            bag_probability({"红": 3}, 1)

    def test_colors_must_be_mapping(self) -> None:
        with self.assertRaises(ValueError):
            bag_probability([("红", 3)], "红")


class SpinnerProbabilityTests(unittest.TestCase):
    def test_repeated_sectors(self) -> None:
        self.assertAlmostEqual(spinner_probability([1, 1, 2, 2], 1), 0.5)
        self.assertAlmostEqual(spinner_probability([1, 1, 2, 2], 2), 0.5)

    def test_single_sector(self) -> None:
        self.assertEqual(spinner_probability([5], 5), 1.0)

    def test_third(self) -> None:
        self.assertAlmostEqual(spinner_probability([1, 2, 3], 3), 1.0 / 3.0)

    def test_empty_sequence(self) -> None:
        with self.assertRaises(ValueError):
            spinner_probability([], 1)

    def test_missing_target(self) -> None:
        with self.assertRaises(ValueError):
            spinner_probability([1, 2], 3)

    def test_invalid_sector_values(self) -> None:
        for sectors in ([True, 1], [1, "2"], "1122"):
            with self.subTest(sectors=sectors):
                with self.assertRaises(ValueError):
                    spinner_probability(sectors, 1)

    def test_invalid_target_type(self) -> None:
        for target in (True, "1", 1.0):
            with self.subTest(target=target):
                with self.assertRaises(ValueError):
                    spinner_probability([1, 2], target)


class ExpectedValueTests(unittest.TestCase):
    def test_fair_coin(self) -> None:
        self.assertAlmostEqual(expected_value([0, 1], [0.5, 0.5]), 0.5)

    def test_weighted_values(self) -> None:
        self.assertAlmostEqual(expected_value([1, 3], [0.25, 0.75]), 2.5)

    def test_fair_die(self) -> None:
        probability = 1.0 / 6.0
        value = expected_value(list(range(1, 7)), [probability] * 6)
        self.assertAlmostEqual(value, 3.5)

    def test_length_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            expected_value([1, 2], [1.0])

    def test_probabilities_must_sum_to_one(self) -> None:
        for probabilities in ([0.5, 0.4], [0.5, 0.500001]):
            with self.subTest(probabilities=probabilities):
                with self.assertRaises(ValueError):
                    expected_value([1, 2], probabilities)

    def test_probability_error_within_tolerance(self) -> None:
        self.assertAlmostEqual(
            expected_value([1, 2], [0.5, 0.5 + 1e-12]), 1.5
        )

    def test_empty_values(self) -> None:
        with self.assertRaises(ValueError):
            expected_value([], [])

    def test_invalid_probability(self) -> None:
        with self.assertRaises(ValueError):
            expected_value([1], [1.1])

    def test_invalid_value(self) -> None:
        with self.assertRaises(ValueError):
            expected_value([True], [1.0])

    def test_non_sequence_inputs(self) -> None:
        for values, probabilities in ((1, [1.0]), ([1], 1.0)):
            with self.subTest(values=values, probabilities=probabilities):
                with self.assertRaises(ValueError):
                    expected_value(values, probabilities)


class CheckAnswerTests(unittest.TestCase):
    def test_exact_match(self) -> None:
        self.assertTrue(check_answer("1/2", "1/2"))

    def test_ignores_spaces(self) -> None:
        self.assertTrue(check_answer(" 1 / 2 ", "1/2"))

    def test_ignores_percent_sign(self) -> None:
        self.assertTrue(check_answer("50％", "50%"))

    def test_accepts_fraction_against_annotated_answer(self) -> None:
        self.assertTrue(check_answer("1/2", "1/2（50%）"))

    def test_rejects_different_value(self) -> None:
        self.assertFalse(check_answer("1/3", "1/2"))

    def test_decimal_is_not_converted_to_fraction(self) -> None:
        self.assertFalse(check_answer("0.5", "1/2"))

    def test_is_case_insensitive(self) -> None:
        self.assertTrue(check_answer("Heads", "heads"))

    def test_rejects_non_string(self) -> None:
        with self.assertRaises(TypeError):
            check_answer(1, "1")
        with self.assertRaises(TypeError):
            check_answer("1", 1)


class MakeQuizTests(unittest.TestCase):
    def test_returns_requested_count(self) -> None:
        self.assertEqual(len(make_quiz(10, 5)), 10)
        self.assertEqual(len(make_quiz(1, 5)), 1)

    def test_item_structure(self) -> None:
        for item in make_quiz(10, 5):
            with self.subTest(item=item):
                self.assertIsInstance(item["question"], str)
                self.assertIsInstance(item["answer"], str)
                self.assertIsInstance(item["options"], list)
                self.assertIsInstance(item["explanation"], str)
                self.assertTrue(item["question"])
                self.assertTrue(item["explanation"])

    def test_four_unique_options_with_answer(self) -> None:
        for item in make_quiz(20, 7):
            options = item["options"]
            self.assertEqual(len(options), 4)
            self.assertEqual(len(set(options)), 4)
            self.assertIn(item["answer"], options)

    def test_same_seed_is_reproducible(self) -> None:
        self.assertEqual(make_quiz(10, 42), make_quiz(10, 42))

    def test_different_seeds_differ(self) -> None:
        self.assertNotEqual(make_quiz(10, 1), make_quiz(10, 2))

    def test_covers_all_topics(self) -> None:
        topics = {item["topic"] for item in make_quiz(10, 3)}
        self.assertEqual(topics, {"coin", "die", "dice", "bag", "spinner"})

    def test_answers_are_formatted(self) -> None:
        for item in make_quiz(10, 4):
            self.assertIn("（", item["answer"])
            self.assertTrue(item["answer"].endswith("%）"))

    def test_count_bounds(self) -> None:
        for count in (0, -1, 101, 1000):
            with self.subTest(count=count):
                with self.assertRaises(ValueError):
                    make_quiz(count, 1)

    def test_count_type(self) -> None:
        for count in (True, 2.0, "10"):
            with self.subTest(count=count):
                with self.assertRaises(ValueError):
                    make_quiz(count, 1)

    def test_seed_type(self) -> None:
        for seed in (True, 1.5, "5"):
            with self.subTest(seed=seed):
                with self.assertRaises(ValueError):
                    make_quiz(5, seed)


if __name__ == "__main__":
    unittest.main()
