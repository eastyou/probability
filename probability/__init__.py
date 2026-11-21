"""probability：面向课堂的简单概率与随机实验小工具。"""

from .model import (
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
from .render import dice_chart_svg, spinner_svg, worksheet_html

__all__ = [
    "bag_probability",
    "check_answer",
    "coin_probability",
    "dice_chart_svg",
    "dice_sum_distribution",
    "dice_sum_probability",
    "die_probability",
    "expected_value",
    "format_probability",
    "make_quiz",
    "spinner_probability",
    "spinner_svg",
    "validate_probability",
    "worksheet_html",
]

__version__ = "0.1.0"
