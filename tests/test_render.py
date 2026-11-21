"""渲染模块单元测试。"""

import unittest

from probability.render import dice_chart_svg, spinner_svg, worksheet_html


class SpinnerSvgTests(unittest.TestCase):
    def test_returns_svg(self) -> None:
        svg = spinner_svg([1, 1, 2, 2])
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))

    def test_draws_one_path_per_sector(self) -> None:
        svg = spinner_svg([1, 1, 2, 2])
        self.assertEqual(svg.count("<path "), 4)

    def test_labels_each_number(self) -> None:
        svg = spinner_svg([1, 1, 2, 2])
        self.assertEqual(svg.count(">1</text>"), 2)
        self.assertEqual(svg.count(">2</text>"), 2)

    def test_single_sector_uses_circle(self) -> None:
        svg = spinner_svg([7])
        self.assertIn("<circle ", svg)
        self.assertIn(">7</text>", svg)

    def test_two_sectors(self) -> None:
        svg = spinner_svg([1, 2])
        self.assertEqual(svg.count("<path "), 2)

    def test_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            spinner_svg([])

    def test_rejects_non_integer_sector(self) -> None:
        with self.assertRaises(ValueError):
            spinner_svg([1, "2"])

    def test_rejects_string_input(self) -> None:
        with self.assertRaises(ValueError):
            spinner_svg("1122")


class DiceChartSvgTests(unittest.TestCase):
    def test_returns_svg(self) -> None:
        svg = dice_chart_svg()
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))

    def test_has_eleven_bars(self) -> None:
        self.assertEqual(dice_chart_svg().count('rx="6"'), 11)

    def test_contains_percentages(self) -> None:
        svg = dice_chart_svg()
        self.assertIn("2.78%", svg)
        self.assertIn("16.67%", svg)

    def test_contains_all_sums(self) -> None:
        svg = dice_chart_svg()
        for total in range(2, 13):
            self.assertIn(">%d</text>" % total, svg)


class WorksheetHtmlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.items = [
            {
                "question": "抛一枚硬币，正面朝上的概率是多少？",
                "options": ["1/2（50%）", "1/3（33.33%）", "1/4（25%）", "1（100%）"],
                "answer": "1/2（50%）",
                "explanation": "硬币两面等可能。",
            },
            {
                "question": "掷一枚骰子，出现 3 的概率是多少？",
                "options": ["1/6（16.67%）", "1/2（50%）", "1/3（33.33%）", "0（0%）"],
                "answer": "1/6（16.67%）",
                "explanation": "六面中只有一面是 3。",
            },
        ]

    def test_returns_complete_html(self) -> None:
        page = worksheet_html(self.items, "概率练习")
        self.assertIn("<!DOCTYPE html>", page)
        self.assertIn('<html lang="zh-CN">', page)
        self.assertIn("</html>", page)

    def test_includes_title_and_questions(self) -> None:
        page = worksheet_html(self.items, "概率练习")
        self.assertIn("概率练习", page)
        self.assertIn("抛一枚硬币", page)
        self.assertIn("掷一枚骰子", page)

    def test_renders_option_letters(self) -> None:
        page = worksheet_html(self.items, "概率练习")
        for letter in ("A.", "B.", "C.", "D."):
            self.assertIn(letter, page)

    def test_hides_answers_by_default(self) -> None:
        page = worksheet_html(self.items, "概率练习")
        self.assertNotIn("答案：", page)
        self.assertIn("答：", page)

    def test_shows_answers_when_requested(self) -> None:
        page = worksheet_html(self.items, "概率练习", show_answers=True)
        self.assertIn("答案：", page)
        self.assertIn("解析：", page)
        self.assertIn("硬币两面等可能。", page)

    def test_has_print_styles(self) -> None:
        page = worksheet_html(self.items, "概率练习")
        self.assertIn("@page", page)
        self.assertIn("size: A4", page)
        self.assertIn("@media print", page)

    def test_escapes_title(self) -> None:
        page = worksheet_html(self.items, "<script>alert(1)</script>")
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertNotIn("<script>alert(1)</script>", page)

    def test_escapes_question_and_options(self) -> None:
        items = [
            {
                "question": "<b>题目</b>",
                "options": ["<i>A</i>", "B", "C", "D"],
                "answer": "<i>A</i>",
                "explanation": "<em>解析</em>",
            }
        ]
        page = worksheet_html(items, "练习", show_answers=True)
        self.assertIn("&lt;b&gt;题目&lt;/b&gt;", page)
        self.assertIn("&lt;i&gt;A&lt;/i&gt;", page)
        self.assertNotIn("<b>题目</b>", page)

    def test_empty_items(self) -> None:
        page = worksheet_html([], "空练习")
        self.assertIn("暂无题目", page)

    def test_rejects_non_sequence_items(self) -> None:
        with self.assertRaises(TypeError):
            worksheet_html("not-a-list", "标题")

    def test_rejects_item_without_question(self) -> None:
        with self.assertRaises(ValueError):
            worksheet_html([{"options": ["A"], "answer": "A"}], "标题")

    def test_rejects_empty_options(self) -> None:
        with self.assertRaises(ValueError):
            worksheet_html([{"question": "题目", "options": [], "answer": "A"}], "标题")

    def test_rejects_non_string_option(self) -> None:
        with self.assertRaises(ValueError):
            worksheet_html([{"question": "题目", "options": [1], "answer": "1"}], "标题")

    def test_rejects_blank_title(self) -> None:
        with self.assertRaises(ValueError):
            worksheet_html([], " ")

    def test_rejects_non_boolean_show_answers(self) -> None:
        with self.assertRaises(ValueError):
            worksheet_html([], "标题", show_answers=1)

    def test_counts_questions_in_footer(self) -> None:
        page = worksheet_html(self.items, "概率练习")
        self.assertIn("共 2 题", page)


if __name__ == "__main__":
    unittest.main()
