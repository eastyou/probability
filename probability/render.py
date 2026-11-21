"""渲染模块：转盘 SVG、骰子分布图和可打印练习纸。"""

from __future__ import annotations

import html
import math
from collections.abc import Mapping
from collections.abc import Sequence as SequenceABC
from typing import Dict, List, Mapping as MappingType, Sequence, Tuple, cast

from .model import _coerce_sectors, dice_sum_distribution

_SVG_START = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 360"'
    ' width="360" height="360" role="img" aria-label="等分转盘">'
)

_PALETTE = (
    "#fca5a5",
    "#fcd34d",
    "#86efac",
    "#93c5fd",
    "#c4b5fd",
    "#f9a8d4",
    "#67e8f9",
    "#fdba74",
)


def _svg_number(value: float) -> str:
    """统一 SVG 坐标的小数位数，避免过长浮点文本。"""
    return "%.2f" % value


def _polar_point(radius: float, angle: float) -> Tuple[float, float]:
    """把角度（以正上方为 0 度、顺时针为正）换算成直角坐标。"""
    radians = math.radians(angle - 90.0)
    return 180.0 + radius * math.cos(radians), 180.0 + radius * math.sin(radians)


def spinner_svg(sectors: Sequence[int]) -> str:
    """生成等面积转盘的 SVG，扇区编号标注在中心附近。"""
    values = _coerce_sectors(sectors)
    count = len(values)
    parts: List[str] = [_SVG_START]
    parts.append('<rect width="360" height="360" fill="#fffdf7"/>')
    if count == 1:
        parts.append(
            '<circle cx="180" cy="180" r="150" fill="%s" stroke="#1f2937"'
            ' stroke-width="2"/>' % _PALETTE[0]
        )
        parts.append(
            '<text x="180" y="180" text-anchor="middle" dominant-baseline="central"'
            ' font-family="PingFang SC, Microsoft YaHei, sans-serif" font-size="26"'
            ' font-weight="700" fill="#111827">%s</text>' % html.escape(str(values[0]))
        )
    else:
        for index, value in enumerate(values):
            span = 360.0 / count
            start = index * span
            end = start + span
            x1, y1 = _polar_point(150.0, start)
            x2, y2 = _polar_point(150.0, end)
            large_arc = 1 if span > 180.0 else 0
            path = (
                "M 180.00 180.00 L %s %s A 150.00 150.00 0 %d 1 %s %s Z"
                % (
                    _svg_number(x1),
                    _svg_number(y1),
                    large_arc,
                    _svg_number(x2),
                    _svg_number(y2),
                )
            )
            parts.append(
                '<path d="%s" fill="%s" stroke="#fffdf7" stroke-width="2"/>'
                % (path, _PALETTE[index % len(_PALETTE)])
            )
            mid_x, mid_y = _polar_point(92.0, start + span / 2.0)
            parts.append(
                '<text x="%s" y="%s" text-anchor="middle" dominant-baseline="central"'
                ' font-family="PingFang SC, Microsoft YaHei, sans-serif" font-size="22"'
                ' font-weight="700" fill="#111827">%s</text>'
                % (
                    _svg_number(mid_x),
                    _svg_number(mid_y),
                    html.escape(str(value)),
                )
            )
    parts.append(
        '<circle cx="180" cy="180" r="150" fill="none" stroke="#1f2937"'
        ' stroke-width="2"/>'
    )
    parts.append("</svg>")
    return "".join(parts)


def dice_chart_svg() -> str:
    """生成两枚骰子点数之和（2~12）的概率柱状图。"""
    distribution: Dict[int, float] = dice_sum_distribution()
    width = 720
    height = 420
    left = 70
    top = 56
    plot_width = width - left - 30
    plot_height = height - top - 60
    baseline = top + plot_height
    slot = plot_width / 11.0
    bar_width = slot * 0.62
    max_probability = 1.0 / 5.0  # 纵轴上限取 20%，为最高的 1/6 留出空间

    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d"'
        ' width="%d" height="%d" role="img" aria-label="两枚骰子点数之和的概率分布">'
        % (width, height, width, height),
        '<rect width="%d" height="%d" fill="#ffffff"/>' % (width, height),
        '<text x="%d" y="32" text-anchor="middle" font-family="PingFang SC,'
        ' Microsoft YaHei, sans-serif" font-size="20" font-weight="700"'
        ' fill="#111827">两枚骰子点数之和的概率分布</text>' % (width // 2),
    ]

    for tick in range(0, 21, 5):
        ratio = tick / 100.0
        y = baseline - (ratio / max_probability) * plot_height
        parts.append(
            '<line x1="%d" y1="%s" x2="%d" y2="%s" stroke="#e5e7eb"'
            ' stroke-width="1"/>'
            % (left, _svg_number(y), width - 30, _svg_number(y))
        )
        parts.append(
            '<text x="%d" y="%s" text-anchor="end" dominant-baseline="central"'
            ' font-family="PingFang SC, Microsoft YaHei, sans-serif" font-size="13"'
            ' fill="#4b5563">%d%%</text>'
            % (left - 10, _svg_number(y), tick)
        )

    parts.append(
        '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#374151" stroke-width="2"/>'
        % (left, baseline, width - 30, baseline)
    )

    for index, total in enumerate(range(2, 13)):
        probability = distribution[total]
        bar_height = probability / max_probability * plot_height
        x = left + index * slot + (slot - bar_width) / 2.0
        y = baseline - bar_height
        parts.append(
            '<rect x="%s" y="%s" width="%s" height="%s" rx="6" fill="%s"/>'
            % (
                _svg_number(x),
                _svg_number(y),
                _svg_number(bar_width),
                _svg_number(bar_height),
                _PALETTE[index % len(_PALETTE)],
            )
        )
        parts.append(
            '<text x="%s" y="%s" text-anchor="middle" font-family="PingFang SC,'
            ' Microsoft YaHei, sans-serif" font-size="12" fill="#374151">%s</text>'
            % (
                _svg_number(x + bar_width / 2.0),
                _svg_number(y - 8),
                _format_percent_text(probability),
            )
        )
        parts.append(
            '<text x="%s" y="%d" text-anchor="middle" font-family="PingFang SC,'
            ' Microsoft YaHei, sans-serif" font-size="15" font-weight="600"'
            ' fill="#111827">%d</text>'
            % (_svg_number(x + bar_width / 2.0), height - 26, total)
        )

    parts.append("</svg>")
    return "".join(parts)


def _format_percent_text(probability: float) -> str:
    """把概率格式化为柱状图顶部的百分数。"""
    text = "%.2f" % (probability * 100.0)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text + "%"


def _normalize_items(
    items: Sequence[MappingType[str, object]],
) -> List[Dict[str, object]]:
    """校验练习纸题目结构，并返回可安全渲染的数据。"""
    if isinstance(items, (str, bytes)) or not isinstance(items, SequenceABC):
        raise TypeError("题目列表必须是序列")
    normalized: List[Dict[str, object]] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, Mapping):
            raise ValueError("第 %d 题必须是字典" % index)
        question = item.get("question")
        if not isinstance(question, str) or not question.strip():
            raise ValueError("第 %d 题缺少 question 文本" % index)
        options = item.get("options")
        if isinstance(options, (str, bytes)) or not isinstance(options, SequenceABC):
            raise ValueError("第 %d 题的 options 必须是选项序列" % index)
        if len(options) == 0:
            raise ValueError("第 %d 题至少需要一个选项" % index)
        option_texts: List[str] = []
        for option in options:
            if not isinstance(option, str):
                raise ValueError("第 %d 题的选项必须是字符串" % index)
            option_texts.append(option)
        answer = item.get("answer", "")
        if not isinstance(answer, str):
            raise ValueError("第 %d 题的 answer 必须是字符串" % index)
        explanation = item.get("explanation", "")
        if not isinstance(explanation, str):
            raise ValueError("第 %d 题的 explanation 必须是字符串" % index)
        normalized.append(
            {
                "question": question,
                "options": option_texts,
                "answer": answer,
                "explanation": explanation,
            }
        )
    return normalized


def _option_letter(index: int) -> str:
    """A、B、C……形式的选项字母。"""
    if index < 26:
        return chr(ord("A") + index)
    return str(index + 1)


def worksheet_html(
    items: Sequence[MappingType[str, object]],
    title: str,
    show_answers: bool = False,
) -> str:
    """生成 A4 可打印练习纸；``show_answers`` 为真时附带答案与解析。"""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("页面标题必须是非空字符串")
    if not isinstance(show_answers, bool):
        raise ValueError("show_answers 必须是布尔值")
    questions = _normalize_items(items)
    safe_title = html.escape(title.strip())

    body: List[str] = []
    body.append("<!DOCTYPE html>")
    body.append('<html lang="zh-CN">')
    body.append("<head>")
    body.append('<meta charset="utf-8">')
    body.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    body.append("<title>%s</title>" % safe_title)
    body.append("<style>")
    body.append(
        """
        * { box-sizing: border-box; }
        body {
            margin: 0;
            padding: 24px 12px;
            background: #eef2f7;
            color: #1f2937;
            font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
            line-height: 1.7;
        }
        .sheet {
            width: 210mm;
            min-height: 297mm;
            margin: 0 auto;
            padding: 18mm 16mm;
            background: #ffffff;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.14);
        }
        .paper-head {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            gap: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid #1f2937;
        }
        h1 { margin: 0; font-size: 24px; letter-spacing: 1px; }
        .brand { font-size: 12px; color: #6b7280; white-space: nowrap; }
        .meta { margin: 10px 0 18px; color: #4b5563; font-size: 14px; }
        .questions { margin: 0; padding: 0; list-style: none; }
        .question-item {
            padding: 14px 0 16px;
            border-bottom: 1px dashed #cbd5e1;
            break-inside: avoid;
        }
        .question { font-size: 16px; font-weight: 600; }
        .number { color: #2563eb; margin-right: 6px; }
        .options {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 6px 20px;
            margin: 10px 0 0;
            padding: 0;
            list-style: none;
            font-size: 15px;
        }
        .letter { color: #6b7280; margin-right: 4px; }
        .workspace { margin-top: 12px; color: #94a3b8; font-size: 14px; }
        .answer {
            margin-top: 10px;
            padding: 10px 12px;
            background: #f0fdf4;
            border-left: 4px solid #22c55e;
            font-size: 14px;
        }
        .answer p { margin: 2px 0; }
        .empty { padding: 28px 0; color: #6b7280; text-align: center; }
        .paper-foot {
            margin-top: 22px;
            padding-top: 10px;
            border-top: 1px solid #e5e7eb;
            color: #9ca3af;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
        }
        @media print {
            body { padding: 0; background: #ffffff; }
            .sheet { width: auto; min-height: auto; padding: 0; box-shadow: none; }
        }
        @page { size: A4; margin: 14mm; }
        """
    )
    body.append("</style>")
    body.append("</head>")
    body.append("<body>")
    body.append('<main class="sheet">')
    body.append('<header class="paper-head">')
    body.append("<h1>%s</h1>" % safe_title)
    body.append('<span class="brand">probability 概率练习</span>')
    body.append("</header>")
    body.append(
        '<p class="meta">姓名：____________　班级：____________　日期：____________</p>'
    )

    if not questions:
        body.append('<p class="empty">暂无题目。</p>')
    else:
        body.append('<ol class="questions">')
        for index, item in enumerate(questions, start=1):
            options = cast(List[str], item["options"])
            body.append('<li class="question-item">')
            body.append(
                '<div class="question"><span class="number">%d.</span>%s</div>'
                % (index, html.escape(str(item["question"])))
            )
            body.append('<ul class="options">')
            for option_index, option in enumerate(options):
                body.append(
                    '<li><span class="letter">%s.</span>%s</li>'
                    % (_option_letter(option_index), html.escape(option))
                )
            body.append("</ul>")
            if show_answers:
                answer = str(item["answer"]) if item["answer"] else "（未提供）"
                body.append('<div class="answer">')
                body.append(
                    "<p><strong>答案：</strong>%s</p>" % html.escape(answer)
                )
                explanation = str(item["explanation"])
                if explanation:
                    body.append(
                        "<p><strong>解析：</strong>%s</p>"
                        % html.escape(explanation)
                    )
                body.append("</div>")
            else:
                body.append('<div class="workspace">答：________________________</div>')
            body.append("</li>")
        body.append("</ol>")

    body.append('<footer class="paper-foot">')
    body.append("<span>probability · 简单概率与随机实验</span>")
    body.append("<span>共 %d 题%s</span>" % (len(questions), "（含答案）" if show_answers else ""))
    body.append("</footer>")
    body.append("</main>")
    body.append("</body>")
    body.append("</html>")
    return "\n".join(body)
