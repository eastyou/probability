# probability

[![CI](https://github.com/eastyou/probability/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/probability/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

面向课堂的简单概率与随机实验工具：硬币、骰子、摸球、转盘，一键生成可打印练习纸。

## 功能

- 硬币正反面概率，支持「正面 / 反面 / heads / tails」与大小写
- 单枚骰子：偶数、奇数、大于 4、小于 3 或指定点数
- 两枚骰子点数之和：基于 36 种等可能结果精确计算，并给出 2~12 的完整分布
- 摸球与转盘：按颜色数量、等面积扇区计算概率
- 概率自动化简为「1/4（25%）」，浮点误差使用容差处理
- 按指定随机种子生成四选一练习，选项唯一且覆盖五类题型
- 生成自包含、内联 CSS、A4 可打印的 HTML 练习纸或答案页
- 纯 Python 标准库，零第三方依赖，兼容 Python 3.9+

## 安装

```bash
pip install -e .
```

也可以不安装，直接在仓库根目录运行 `python -m probability`。

## 使用

```bash
# 硬币
probability coin 正面                    # 正面 的概率 = 1/2（50%）
probability coin heads                   # heads 的概率 = 1/2（50%）

# 单枚骰子
probability die 偶数                     # 「偶数」的概率 = 1/2（50%）
probability die 大于4                    # 「大于4」的概率 = 1/3（33.33%）
probability die 3                        # 「3」的概率 = 1/6（16.67%）

# 两枚骰子点数之和
probability dice 7                       # 两枚骰子点数之和为 7 的概率 = 1/6（16.67%）
probability dice 12                      # 两枚骰子点数之和为 12 的概率 = 1/36（2.78%）

# 摸球
probability bag "红:3,蓝:1" 红            # 摸到红的概率 = 3/4（75%）

# 转盘
probability spinner "1,1,2,2" 1          # 指针停在编号 1 的概率 = 1/2（50%）

# 生成练习纸（可加 --answers 生成答案页）
probability quiz --count 10 --seed 5 -o examples/worksheet.html
probability quiz --count 10 --seed 5 --answers -o examples/answers.html

# 生成示例练习纸
probability demo -o examples/demo.html
```

## 作为库使用

```python
from probability import (
    coin_probability,
    dice_sum_distribution,
    format_probability,
    make_quiz,
    spinner_probability,
)

assert format_probability(coin_probability("正面")) == "1/2（50%）"
assert format_probability(spinner_probability([1, 1, 2, 2], 1)) == "1/2（50%）"
assert abs(dice_sum_distribution()[7] - 1 / 6) < 1e-12

items = make_quiz(10, seed=5)
assert len(items) == 10
assert all(len(item["options"]) == 4 for item in items)
```

## 示例

[examples/worksheet.html](examples/worksheet.html) 是由
`probability quiz --count 10 --seed 5 --answers -o examples/worksheet.html`
生成的答案页，包含 10 道四选一概率题、答案与解析，可直接用浏览器打印为 A4 练习纸。

## 测试

```bash
python -m unittest discover -s tests -v
```

共 133 项单元测试，覆盖概率校验、化简与格式化、硬币/骰子/摸球/转盘概率、点数和的分布与对称性、期望值、练习生成与可复现性、SVG 与 HTML 渲染、HTML 转义以及命令行退出码。CI 在 Linux、macOS、Windows 上运行 Python 3.9 ~ 3.13。

## 许可

MIT © 2026 eastyou
