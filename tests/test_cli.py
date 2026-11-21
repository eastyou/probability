"""命令行入口单元测试。"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from typing import List, Tuple

from probability.cli import main


def run_cli(arguments: List[str]) -> Tuple[int, str, str]:
    """执行命令行并捕获标准输出与标准错误。"""
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(arguments)
    return code, stdout.getvalue(), stderr.getvalue()


class CoinCommandTests(unittest.TestCase):
    def test_coin_success(self) -> None:
        code, stdout, stderr = run_cli(["coin", "正面"])
        self.assertEqual(code, 0)
        self.assertIn("1/2（50%）", stdout)
        self.assertEqual(stderr, "")

    def test_coin_english_alias(self) -> None:
        code, stdout, _ = run_cli(["coin", "heads"])
        self.assertEqual(code, 0)
        self.assertIn("1/2（50%）", stdout)

    def test_coin_invalid_face(self) -> None:
        code, stdout, stderr = run_cli(["coin", "侧面"])
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr.startswith("错误："))


class DieCommandTests(unittest.TestCase):
    def test_die_even(self) -> None:
        code, stdout, _ = run_cli(["die", "偶数"])
        self.assertEqual(code, 0)
        self.assertIn("1/2（50%）", stdout)

    def test_die_specific_face(self) -> None:
        code, stdout, _ = run_cli(["die", "3"])
        self.assertEqual(code, 0)
        self.assertIn("1/6（16.67%）", stdout)

    def test_die_invalid_condition(self) -> None:
        code, _, stderr = run_cli(["die", "等于3"])
        self.assertEqual(code, 2)
        self.assertTrue(stderr.startswith("错误："))


class DiceCommandTests(unittest.TestCase):
    def test_dice_seven(self) -> None:
        code, stdout, _ = run_cli(["dice", "7"])
        self.assertEqual(code, 0)
        self.assertIn("1/6（16.67%）", stdout)

    def test_dice_two(self) -> None:
        code, stdout, _ = run_cli(["dice", "2"])
        self.assertEqual(code, 0)
        self.assertIn("1/36（2.78%）", stdout)

    def test_dice_out_of_range(self) -> None:
        code, _, stderr = run_cli(["dice", "13"])
        self.assertEqual(code, 2)
        self.assertTrue(stderr.startswith("错误："))


class BagCommandTests(unittest.TestCase):
    def test_bag_success(self) -> None:
        code, stdout, _ = run_cli(["bag", "红:3,蓝:1", "红"])
        self.assertEqual(code, 0)
        self.assertIn("3/4（75%）", stdout)

    def test_bag_accepts_chinese_comma(self) -> None:
        code, stdout, _ = run_cli(["bag", "红：2，蓝：2", "蓝"])
        self.assertEqual(code, 0)
        self.assertIn("1/2（50%）", stdout)

    def test_bag_missing_target(self) -> None:
        code, _, stderr = run_cli(["bag", "红:3", "蓝"])
        self.assertEqual(code, 2)
        self.assertIn("没有颜色", stderr)

    def test_bag_malformed_spec(self) -> None:
        for spec in ("红3", "红:1,红:2", "红:x", ""):
            with self.subTest(spec=spec):
                code, _, stderr = run_cli(["bag", spec, "红"])
                self.assertEqual(code, 2)
                self.assertTrue(stderr.startswith("错误："))


class SpinnerCommandTests(unittest.TestCase):
    def test_spinner_success(self) -> None:
        code, stdout, _ = run_cli(["spinner", "1,1,2,2", "1"])
        self.assertEqual(code, 0)
        self.assertIn("1/2（50%）", stdout)

    def test_spinner_missing_target(self) -> None:
        code, _, stderr = run_cli(["spinner", "1,2,3", "4"])
        self.assertEqual(code, 2)
        self.assertIn("没有编号", stderr)

    def test_spinner_malformed_sectors(self) -> None:
        for spec in ("1,a", "1,,2", ""):
            with self.subTest(spec=spec):
                code, _, stderr = run_cli(["spinner", spec, "1"])
                self.assertEqual(code, 2)
                self.assertTrue(stderr.startswith("错误："))


class QuizCommandTests(unittest.TestCase):
    def test_quiz_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "worksheet.html")
            code, stdout, stderr = run_cli(
                ["quiz", "--count", "4", "--seed", "5", "-o", output]
            )
            self.assertEqual(code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("已生成练习纸", stdout)
            self.assertTrue(os.path.exists(output))
            with open(output, "r", encoding="utf-8") as handle:
                page = handle.read()
            self.assertIn("<!DOCTYPE html>", page)
            self.assertIn("概率练习纸", page)
            self.assertEqual(page.count('class="question-item"'), 4)
            self.assertNotIn("答案：", page)

    def test_quiz_with_answers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "answers.html")
            code, _, _ = run_cli(
                ["quiz", "--count", "3", "--seed", "1", "--answers", "-o", output]
            )
            self.assertEqual(code, 0)
            with open(output, "r", encoding="utf-8") as handle:
                page = handle.read()
            self.assertIn("答案：", page)
            self.assertIn("解析：", page)
            self.assertIn("（含答案）", page)

    def test_quiz_custom_title(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "titled.html")
            code, _, _ = run_cli(
                ["quiz", "--count", "1", "--seed", "1", "-o", output, "--title", "单元练习"]
            )
            self.assertEqual(code, 0)
            with open(output, "r", encoding="utf-8") as handle:
                self.assertIn("单元练习", handle.read())

    def test_quiz_invalid_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "bad.html")
            code, _, stderr = run_cli(
                ["quiz", "--count", "0", "--seed", "1", "-o", output]
            )
            self.assertEqual(code, 2)
            self.assertTrue(stderr.startswith("错误："))
            self.assertFalse(os.path.exists(output))

    def test_quiz_creates_parent_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "nested", "deep", "worksheet.html")
            code, _, _ = run_cli(
                ["quiz", "--count", "2", "--seed", "2", "-o", output]
            )
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(output))


class DemoCommandTests(unittest.TestCase):
    def test_demo_creates_eight_questions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "demo.html")
            code, stdout, _ = run_cli(["demo", "-o", output])
            self.assertEqual(code, 0)
            self.assertIn("已生成示例练习纸", stdout)
            with open(output, "r", encoding="utf-8") as handle:
                page = handle.read()
            self.assertIn("概率演示练习纸", page)
            self.assertEqual(page.count('class="question-item"'), 8)

    def test_demo_with_answers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "demo-answers.html")
            code, _, _ = run_cli(["demo", "--answers", "-o", output])
            self.assertEqual(code, 0)
            with open(output, "r", encoding="utf-8") as handle:
                page = handle.read()
            self.assertIn("答案：", page)

    def test_demo_invalid_seed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "bad-seed.html")
            code, _, stderr = run_cli(["demo", "--seed", "abc", "-o", output])
            self.assertEqual(code, 2)
            self.assertNotEqual(stderr, "")


class ParserTests(unittest.TestCase):
    def test_help_exits_zero(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout), self.assertRaises(SystemExit) as context:
            main(["--help"])
        self.assertEqual(context.exception.code, 0)
        self.assertIn("probability", stdout.getvalue())

    def test_missing_command_exits_with_error(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as context:
            main([])
        self.assertEqual(context.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
