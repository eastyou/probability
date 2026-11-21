"""probability 命令行入口。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from .model import (
    bag_probability,
    coin_probability,
    dice_sum_probability,
    die_probability,
    format_probability,
    make_quiz,
    spinner_probability,
)
from .render import worksheet_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="probability",
        description="简单概率与随机实验：硬币、骰子、摸球、转盘与练习纸",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    coin = sub.add_parser("coin", help="计算硬币某一面的概率")
    coin.add_argument("face", help="正面 / 反面 / heads / tails")

    die = sub.add_parser("die", help="计算单枚骰子满足条件的概率")
    die.add_argument("kind", help="偶数 / 奇数 / 大于4 / 小于3 / 1~6")

    dice = sub.add_parser("dice", help="计算两枚骰子点数和的概率")
    dice.add_argument("total", help="点数和，范围 2~12")

    bag = sub.add_parser("bag", help="按袋中颜色数量计算摸球概率")
    bag.add_argument("colors", help="颜色与数量，例如 红:3,蓝:1")
    bag.add_argument("target", help="目标颜色")

    spinner = sub.add_parser("spinner", help="计算等面积转盘停在某编号的概率")
    spinner.add_argument("sectors", help="扇区编号，例如 1,1,2,2")
    spinner.add_argument("target", help="目标编号")

    quiz = sub.add_parser("quiz", help="生成可打印的概率练习纸")
    quiz.add_argument("--count", default=10, help="题目数量，范围 1~100")
    quiz.add_argument("--seed", default=0, help="随机种子")
    quiz.add_argument("-o", "--output", required=True, help="输出 HTML 路径")
    quiz.add_argument("--answers", action="store_true", help="显示答案与解析")
    quiz.add_argument("--title", default="概率练习纸", help="页面标题")

    demo = sub.add_parser("demo", help="生成一份示例练习纸")
    demo.add_argument("-o", "--output", required=True, help="输出 HTML 路径")
    demo.add_argument("--seed", default=2026, help="随机种子")
    demo.add_argument("--answers", action="store_true", help="显示答案与解析")

    return parser


def _to_int(value: object, label: str) -> int:
    """把命令行文本转换为整数，并给出中文错误提示。"""
    if isinstance(value, bool):
        raise ValueError("%s必须是整数" % label)
    if isinstance(value, int):
        return value
    if not isinstance(value, str) or not value.strip():
        raise ValueError("%s必须是非空整数" % label)
    try:
        return int(value.strip())
    except ValueError:
        raise ValueError("%s必须是整数，收到「%s」" % (label, value))


def _parse_bag_spec(text: str) -> Dict[str, int]:
    """解析「红:3,蓝:1」形式的袋中颜色配置。"""
    if not isinstance(text, str):
        raise ValueError("袋中颜色配置必须是字符串")
    source = text.strip()
    if not source:
        raise ValueError("袋中颜色配置不能为空，例如 红:3,蓝:1")
    parts: List[str] = re.split(r"[,，;；]", source)
    colors: Dict[str, int] = {}
    for part in parts:
        item = part.strip()
        if not item:
            raise ValueError("颜色配置格式应为 红:3,蓝:1")
        pair = re.split(r"[:：]", item)
        if len(pair) != 2:
            raise ValueError("颜色配置格式应为 红:3,蓝:1，收到「%s」" % item)
        color = pair[0].strip()
        count_text = pair[1].strip()
        if not color:
            raise ValueError("颜色名称不能为空")
        if color in colors:
            raise ValueError("颜色「%s」重复出现" % color)
        try:
            count = int(count_text)
        except (TypeError, ValueError):
            raise ValueError("颜色「%s」的数量必须是整数" % color)
        colors[color] = count
    return colors


def _parse_sectors(text: str) -> List[int]:
    """解析「1,1,2,2」形式的转盘扇区编号。"""
    if not isinstance(text, str):
        raise ValueError("转盘扇区必须是字符串")
    source = text.strip()
    if not source:
        raise ValueError("转盘扇区不能为空，例如 1,1,2,2")
    parts: List[str] = re.split(r"[,，;；]", source)
    sectors: List[int] = []
    for part in parts:
        item = part.strip()
        if not item:
            raise ValueError("扇区编号必须是整数列表，例如 1,1,2,2")
        try:
            sectors.append(int(item))
        except (TypeError, ValueError):
            raise ValueError("扇区编号必须是整数，收到「%s」" % item)
    return sectors


def _write_html(path: str, content: str) -> Path:
    """把 HTML 写入目标路径，必要时创建父目录。"""
    if not isinstance(path, str) or not path.strip():
        raise ValueError("输出路径不能为空")
    output = Path(path.strip())
    if str(output.parent) not in ("", "."):
        output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    return output


def _run(args: argparse.Namespace) -> int:
    if args.command == "coin":
        probability = coin_probability(args.face)
        print("%s 的概率 = %s" % (args.face, format_probability(probability)))
        return 0
    if args.command == "die":
        probability = die_probability(args.kind)
        print("「%s」的概率 = %s" % (args.kind, format_probability(probability)))
        return 0
    if args.command == "dice":
        total = _to_int(args.total, "点数和")
        probability = dice_sum_probability(total)
        print(
            "两枚骰子点数之和为 %d 的概率 = %s"
            % (total, format_probability(probability))
        )
        return 0
    if args.command == "bag":
        colors = _parse_bag_spec(args.colors)
        probability = bag_probability(colors, args.target)
        print(
            "摸到%s的概率 = %s" % (args.target, format_probability(probability))
        )
        return 0
    if args.command == "spinner":
        sectors = _parse_sectors(args.sectors)
        target = _to_int(args.target, "目标编号")
        probability = spinner_probability(sectors, target)
        print(
            "指针停在编号 %d 的概率 = %s"
            % (target, format_probability(probability))
        )
        return 0
    if args.command == "quiz":
        count = _to_int(args.count, "题目数量")
        seed = _to_int(args.seed, "随机种子")
        items = make_quiz(count, seed)
        page = worksheet_html(items, args.title, show_answers=args.answers)
        output = _write_html(args.output, page)
        suffix = "，含答案" if args.answers else ""
        print("已生成练习纸：%s（%d 题%s）" % (output, len(items), suffix))
        return 0
    if args.command == "demo":
        seed = _to_int(args.seed, "随机种子")
        items = make_quiz(8, seed)
        page = worksheet_html(items, "概率演示练习纸", show_answers=args.answers)
        output = _write_html(args.output, page)
        print("已生成示例练习纸：%s（%d 题）" % (output, len(items)))
        return 0
    raise ValueError("未知命令：%s" % args.command)


def _ensure_utf8_console() -> None:
    """Windows 控制台默认编码可能无法输出中文，尽量切换为 UTF-8。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            continue


def main(argv: Optional[Sequence[str]] = None) -> int:
    _ensure_utf8_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except (TypeError, ValueError) as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
