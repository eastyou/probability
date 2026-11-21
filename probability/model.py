"""概率计算核心模型：硬币、骰子、摸球、转盘与随机练习。

所有对外函数都会校验外部输入，非法输入统一抛出 ``ValueError``，
以保证命令行和库调用得到一致的中文错误提示。
"""

from __future__ import annotations

import math
import random
from collections.abc import Mapping
from collections.abc import Sequence as SequenceABC
from fractions import Fraction
from typing import Dict, List, Sequence

TOLERANCE = 1e-9
_MAX_DENOMINATOR = 10000
_MIN_QUIZ_COUNT = 1
_MAX_QUIZ_COUNT = 100

_COIN_FACES = ("正面", "反面")
_COIN_ALIASES = {
    "正面": 0.5,
    "反面": 0.5,
    "heads": 0.5,
    "tails": 0.5,
}
_COLORS = ("红", "蓝", "绿", "黄")
_QUIZ_TOPICS = ("coin", "die", "dice", "bag", "spinner")

_OPTION_VALUES = (
    0.0,
    1.0 / 36.0,
    1.0 / 18.0,
    1.0 / 12.0,
    1.0 / 9.0,
    1.0 / 8.0,
    1.0 / 6.0,
    5.0 / 36.0,
    1.0 / 4.0,
    1.0 / 3.0,
    5.0 / 12.0,
    1.0 / 2.0,
    7.0 / 12.0,
    2.0 / 3.0,
    3.0 / 4.0,
    1.0,
)


def validate_probability(value: float) -> float:
    """校验并返回 0~1 之间的有限概率值。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("概率必须是数字，不能是布尔值或其他类型")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("概率必须是有限数字，不能是 NaN 或无穷大")
    if number < 0.0 or number > 1.0:
        raise ValueError("概率必须在 0 到 1 之间，收到 %r" % value)
    return number


def _format_percent(value: float) -> str:
    """把 0~1 的概率格式化成不带多余零的百分数。"""
    text = "%.2f" % (value * 100.0)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def format_probability(value: float) -> str:
    """化简概率为「1/4（25%）」形式，并对浮点误差做容差处理。"""
    number = validate_probability(value)
    fraction = Fraction(number).limit_denominator(_MAX_DENOMINATOR)
    if abs(float(fraction) - number) > TOLERANCE:
        decimal_text = ("%.4f" % number).rstrip("0").rstrip(".")
        if decimal_text in ("", "-0"):
            decimal_text = "0"
        return "%s（%s%%）" % (decimal_text, _format_percent(number))
    if fraction.denominator == 1:
        fraction_text = str(fraction.numerator)
    else:
        fraction_text = "%d/%d" % (fraction.numerator, fraction.denominator)
    return "%s（%s%%）" % (fraction_text, _format_percent(float(fraction)))


def coin_probability(face: str) -> float:
    """返回硬币某一面的概率；支持中英文与大小写。"""
    if not isinstance(face, str):
        raise ValueError("硬币面必须是字符串，例如 正面 或 heads")
    key = face.strip().lower()
    if key not in _COIN_ALIASES:
        raise ValueError("无法识别的硬币面：%s（可用 正面/反面/heads/tails）" % face)
    return _COIN_ALIASES[key]


def _die_favorable_count(kind: str) -> int:
    """返回单枚骰子满足条件的点数个数。"""
    if not isinstance(kind, str):
        raise ValueError("骰子条件必须是字符串")
    text = "".join(kind.split())
    counts = {"偶数": 3, "奇数": 3, "大于4": 2, "小于3": 2}
    if text in counts:
        return counts[text]
    if text.isdigit():
        face = int(text)
        if 1 <= face <= 6:
            return 1
        raise ValueError("骰子点数必须在 1 到 6 之间，收到 %s" % kind)
    raise ValueError(
        "无法识别的骰子条件：%s（可用 偶数/奇数/大于4/小于3/1~6）" % kind
    )


def die_probability(kind: str) -> float:
    """返回单枚公平六面骰满足某条件的概率。"""
    return _die_favorable_count(kind) / 6.0


def _dice_sum_counts() -> Dict[int, int]:
    """枚举两枚骰子的 36 种等可能结果，统计点数和的出现次数。"""
    counts: Dict[int, int] = {}
    for first in range(1, 7):
        for second in range(1, 7):
            total = first + second
            counts[total] = counts.get(total, 0) + 1
    return counts


def dice_sum_probability(total: int) -> float:
    """返回两枚公平六面骰点数之和为 ``total`` 的概率。"""
    if isinstance(total, bool) or not isinstance(total, int):
        raise ValueError("点数和必须是整数")
    if total < 2 or total > 12:
        raise ValueError("两枚骰子的点数和必须在 2 到 12 之间，收到 %d" % total)
    return _dice_sum_counts()[total] / 36.0


def dice_sum_distribution() -> Dict[int, float]:
    """返回 2~12 每个点数和对应的概率，概率之和为 1。"""
    return {total: count / 36.0 for total, count in sorted(_dice_sum_counts().items())}


def _validate_color_counts(colors: Dict[str, int]) -> Dict[str, int]:
    """校验袋中颜色与数量，返回规范化后的副本。"""
    if not isinstance(colors, Mapping):
        raise ValueError("袋中颜色必须是「颜色:数量」的字典")
    if not colors:
        raise ValueError("袋中至少要有一个球")
    normalized: Dict[str, int] = {}
    for color, count in colors.items():
        if not isinstance(color, str) or not color.strip():
            raise ValueError("颜色名称必须是非空字符串")
        if isinstance(count, bool) or not isinstance(count, int):
            raise ValueError("颜色「%s」的数量必须是整数" % color)
        if count <= 0:
            raise ValueError("颜色「%s」的数量必须是正整数" % color)
        key = color.strip()
        if key in normalized:
            raise ValueError("颜色「%s」重复出现" % key)
        normalized[key] = count
    return normalized


def bag_probability(colors: Dict[str, int], target: str) -> float:
    """从袋中随机摸一个球，返回摸到 ``target`` 颜色的概率。"""
    normalized = _validate_color_counts(colors)
    if not isinstance(target, str) or not target.strip():
        raise ValueError("目标颜色必须是非空字符串")
    key = target.strip()
    if key not in normalized:
        raise ValueError("袋中没有颜色「%s」" % target)
    total = sum(normalized.values())
    return normalized[key] / float(total)


def _coerce_sectors(sectors: Sequence[int]) -> List[int]:
    """校验转盘扇区编号，返回整数列表。"""
    if isinstance(sectors, (str, bytes)) or not isinstance(sectors, SequenceABC):
        raise ValueError("转盘扇区必须是非空的整数序列")
    if len(sectors) == 0:
        raise ValueError("转盘至少需要一个扇区")
    values: List[int] = []
    for sector in sectors:
        if isinstance(sector, bool) or not isinstance(sector, int):
            raise ValueError("转盘扇区编号必须是整数")
        values.append(sector)
    return values


def spinner_probability(sectors: Sequence[int], target: int) -> float:
    """等面积转盘停在编号 ``target`` 上的概率。"""
    values = _coerce_sectors(sectors)
    if isinstance(target, bool) or not isinstance(target, int):
        raise ValueError("转盘目标编号必须是整数")
    if target not in values:
        raise ValueError("转盘上没有编号 %d" % target)
    return values.count(target) / float(len(values))


def expected_value(
    values: Sequence[int], probabilities: Sequence[float]
) -> float:
    """按给定概率求期望值，要求概率之和约为 1。"""
    if (
        isinstance(values, (str, bytes))
        or not isinstance(values, SequenceABC)
        or isinstance(probabilities, (str, bytes))
        or not isinstance(probabilities, SequenceABC)
    ):
        raise ValueError("取值与概率都必须是序列")
    if len(values) == 0:
        raise ValueError("至少需要一个取值")
    if len(values) != len(probabilities):
        raise ValueError("取值与概率的长度必须一致")
    normalized: List[float] = []
    for probability in probabilities:
        normalized.append(validate_probability(probability))
    if abs(sum(normalized) - 1.0) > TOLERANCE:
        raise ValueError("所有概率之和必须约等于 1")
    total = 0.0
    for value, probability in zip(values, normalized):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("取值必须是数字")
        if not math.isfinite(float(value)):
            raise ValueError("取值必须是有限数字")
        total += float(value) * probability
    return total


def _normalize_answer(value: str) -> str:
    """去掉空白、百分号与百分比括号，只保留核心答案文本。"""
    text = value.replace("％", "%").replace("　", " ")
    text = "".join(text.split())
    text = text.replace("%", "")
    text = text.replace("（", "(").replace("）", ")")
    if "(" in text:
        text = text.split("(", 1)[0]
    return text.lower()


def check_answer(answer: str, expected: str) -> bool:
    """判断题答案是否与标准答案一致（仅做字符串规范化）。"""
    if not isinstance(answer, str) or not isinstance(expected, str):
        raise TypeError("答案必须是字符串")
    return _normalize_answer(answer) == _normalize_answer(expected)


def _make_options(answer: str, rng: random.Random) -> List[str]:
    """构造四个互不相同的选项，并保证标准答案在其中。"""
    candidates = [
        format_probability(value) for value in _OPTION_VALUES
    ]
    candidates = list(dict.fromkeys(option for option in candidates if option != answer))
    if len(candidates) < 3:
        raise ValueError("可用的选项数量不足")
    options = [answer] + rng.sample(candidates, 3)
    rng.shuffle(options)
    return options


def _quiz_coin(rng: random.Random) -> Dict[str, object]:
    face = rng.choice(_COIN_FACES)
    answer = format_probability(coin_probability(face))
    return {
        "topic": "coin",
        "question": "抛一枚均匀硬币，%s朝上的概率是多少？" % face,
        "answer": answer,
        "options": _make_options(answer, rng),
        "explanation": "硬币只有正、反两种等可能结果，符合条件的只有 1 种，所以概率是 1/2。",
    }


def _quiz_die(rng: random.Random) -> Dict[str, object]:
    kind = rng.choice(("偶数", "奇数", "大于4", "小于3", "1", "2", "3", "4", "5", "6"))
    count = _die_favorable_count(kind)
    answer = format_probability(die_probability(kind))
    if kind.isdigit():
        question = "掷一枚均匀的六面骰子，点数正好是 %s 的概率是多少？" % kind
    else:
        question = "掷一枚均匀的六面骰子，点数满足「%s」的概率是多少？" % kind
    return {
        "topic": "die",
        "question": question,
        "answer": answer,
        "options": _make_options(answer, rng),
        "explanation": "六面骰子共有 6 种等可能结果，满足条件的有 %d 种。" % count,
    }


def _quiz_dice(rng: random.Random) -> Dict[str, object]:
    total = rng.randint(2, 12)
    count = _dice_sum_counts()[total]
    answer = format_probability(dice_sum_probability(total))
    return {
        "topic": "dice",
        "question": "同时掷两枚均匀的六面骰子，点数之和为 %d 的概率是多少？" % total,
        "answer": answer,
        "options": _make_options(answer, rng),
        "explanation": "两枚骰子共有 36 种等可能结果，点数之和为 %d 的有 %d 种。" % (total, count),
    }


def _quiz_bag(rng: random.Random) -> Dict[str, object]:
    names = rng.sample(list(_COLORS), rng.randint(2, 3))
    colors: Dict[str, int] = {name: rng.randint(1, 4) for name in names}
    target = rng.choice(names)
    total = sum(colors.values())
    answer = format_probability(bag_probability(colors, target))
    description = "、".join("%s %d 个" % (name, colors[name]) for name in names)
    return {
        "topic": "bag",
        "question": "袋中有%s球，大小质地相同。随机摸出一个球，摸到%s球的概率是多少？"
        % (description, target),
        "answer": answer,
        "options": _make_options(answer, rng),
        "explanation": "袋中共有 %d 个球，其中%s球 %d 个，所以概率是 %d/%d。"
        % (total, target, colors[target], colors[target], total),
    }


def _quiz_spinner(rng: random.Random) -> Dict[str, object]:
    sector_count = rng.randint(4, 6)
    sectors = [rng.randint(1, 4) for _ in range(sector_count)]
    target = rng.choice(sectors)
    answer = format_probability(spinner_probability(sectors, target))
    labels = ",".join(str(sector) for sector in sectors)
    return {
        "topic": "spinner",
        "question": "转盘被等分为 %d 个面积相同的扇区，编号依次为 %s。指针停在编号 %d 的概率是多少？"
        % (len(sectors), labels, target),
        "answer": answer,
        "options": _make_options(answer, rng),
        "explanation": "转盘共有 %d 个等面积扇区，编号 %d 出现了 %d 次，所以概率是 %d/%d。"
        % (len(sectors), target, sectors.count(target), sectors.count(target), len(sectors)),
    }


_QUIZ_GENERATORS = {
    "coin": _quiz_coin,
    "die": _quiz_die,
    "dice": _quiz_dice,
    "bag": _quiz_bag,
    "spinner": _quiz_spinner,
}


def make_quiz(count: int, seed: int) -> List[Dict[str, object]]:
    """生成可复现的四选一概率练习，覆盖硬币、单骰、双骰、摸球和转盘。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise ValueError("题目数量必须是整数")
    if count < _MIN_QUIZ_COUNT or count > _MAX_QUIZ_COUNT:
        raise ValueError(
            "题目数量必须在 %d 到 %d 之间，收到 %d"
            % (_MIN_QUIZ_COUNT, _MAX_QUIZ_COUNT, count)
        )
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("随机种子必须是整数")
    rng = random.Random(seed)
    topics = [_QUIZ_TOPICS[index % len(_QUIZ_TOPICS)] for index in range(count)]
    rng.shuffle(topics)
    items: List[Dict[str, object]] = []
    for topic in topics:
        items.append(_QUIZ_GENERATORS[topic](rng))
    return items
