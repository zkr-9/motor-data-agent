# ⚡ 电机实验数据智能处理与可视化 AI Agent

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 面向电气工程专业的三相异步电机实验数据智能分析 Agent — 基于 OpenAI Function Calling, 支持自然语言交互、自动异常检测、专业可视化。

---

## 📸 效果预览

```
👤 你: 帮我加载数据，看看有没有异常

🔧 调用工具: load_motor_data({'filepath': 'data/motor_data.csv'})
🔧 调用工具: detect_anomalies({})

🤖 Agent: 数据加载完成，共200个采样点。异常检测结果如下：

⚠ 过流: 15处 (主要出现在 t>160s 区域，伴随严重故障标记)
⚠ 振动超标: 23处 (t=80~120s 轴承早期磨损, t>160s 急剧恶化)  
⚠ 转速骤降: 8处 (与过流时段高度重合)
✅ 电压跌落: 未检出
✅ 过热: 未检出

**专业诊断**: t>160s 的异常模式（过流+振动超标+转速骤降）
高度提示匝间短路故障，建议停机检查定子绕组绝缘电阻。
```

---

## 🏗 项目架构

```
motor-experiment-ai-agent/
├── main.py                    # 程序入口 (交互/一键/数据生成)
├── config.py                  # 全局配置 (API Key / 路径 / 参数)
├── requirements.txt           # Python 依赖
├── .env.example               # 环境变量模板
├── README.md
│
├── agent/                     # 🤖 AI Agent 核心
│   ├── core.py               #   ReAct 循环 + Function Calling
│   ├── tools.py              #   工具定义与执行 (5 个工具)
│   └── prompts.py            #   系统提示词 (电机专家角色)
│
├── data/                      # 📊 数据层
│   ├── sample_generator.py   #   仿真三相异步电机实验数据生成
│   └── motor_data.csv        #   样本数据 (运行后生成)
│
├── visualization/             # 📈 可视化层
│   └── plotter.py            #   matplotlib 专业绘图 (3 类图表)
│
├── utils/                     # 🔧 工具层
│   └── motor_analysis.py     #   统计分析 / 异常检测 / 报告生成
│
└── output/                    # 🖼 图表输出目录 (运行后生成)
    ├── 00_overview.png       #   综合概览图 (6 通道子图)
    ├── 01_efficiency_curve.png # 效率-负载特性曲线
    └── 02_anomaly_dashboard.png # 异常检测仪表盘
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone https://github.com/你的用户名/motor-experiment-ai-agent.git
cd motor-experiment-ai-agent

# 安装依赖 (需要 Python 3.9+)
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入你的 OpenAI API Key (或兼容端点)
# OPENAI_API_KEY=sk-xxxxx
# OPENAI_BASE_URL=https://api.openai.com/v1   # 可替换为其他兼容 API
# OPENAI_MODEL=gpt-4o-mini
```

### 3. 运行

```bash
# 方式一: 交互对话模式 (最灵活)
python main.py

# 方式二: 一键自动分析 (演示用)
python main.py --quick

# 方式三: 仅生成样本数据
python main.py --generate-data
```

---

## 🛠 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **AI Agent** | OpenAI Function Calling | 自然语言理解 + 工具调用 (ReAct 模式) |
| **数据分析** | Pandas + NumPy + SciPy | 统计量计算、异常检测算法 |
| **可视化** | Matplotlib | 6 通道综合概览图、效率曲线、异常仪表盘 |
| **数据仿真** | NumPy (随机过程) | 生成贴近真实的三相异步电机实验数据 |

---

## 📊 仿真数据说明

生成的样本数据模拟一台 **Y 系列三相异步电动机** (4 极, 50Hz, 同步转速 1500rpm) 的完整实验过程:

| 字段 | 范围 | 说明 |
|------|------|------|
| `voltage_V` | 380V ±2% | 三相平均线电压 |
| `current_A` | 0.8A→4.5A | 定子电流 (空载→满载) |
| `speed_rpm` | 1498→1440 | 转速 (转差率 0.1%→4%) |
| `torque_Nm` | 0.05→5.0 | 电磁转矩 |
| `power_W` | — | 输入功率 P=√3·U·I·cosφ |
| `temperature_C` | 25→75 | 绕组温度 (指数上升) |
| `vibration_mm/s` | 1.2→10 | 振动烈度 (ISO 10816) |
| `fault_flag` | 0/1/2 | 正常 / 轻微异常 / 严重异常 |

数据中模拟了两种典型故障:
- **t=80~120s**: 轴承早期磨损 → 振动逐步升高
- **t>160s**: 匝间短路 → 电流突增 + 温度骤升 + 振动剧烈

---

## 🤖 Agent 工具列表

| 工具 | 功能 |
|------|------|
| `load_motor_data` | 加载 CSV 数据文件 |
| `get_basic_stats` | 电气/机械参数统计 + 效率估算 |
| `detect_anomalies` | 基于专业判据的异常检测 |
| `generate_plots` | 一键生成 3 张专业图表 |
| `full_report` | 生成完整文字分析报告 |

---

## 📝 使用示例

```
👤 你: 加载 data/motor_data.csv，帮我看看有没有过流

🤖 Agent: 已加载 200 个采样点。我检测到 15 处过流 (>4.2A)，
主要集中在 t>160s 区域，同时伴随严重故障标记。
电流峰值达到 4.85A（t=185s），建议检查该时段的定子绕组状态。
需要我生成异常检测仪表盘来直观展示吗？

👤 你: 好，出图吧

🤖 Agent: [生成图表] 已生成 3 张图表到 output/ 目录：
- 00_overview.png (6通道综合概览)
- 01_efficiency_curve.png (效率-负载曲线)
- 02_anomaly_dashboard.png (异常检测仪表盘)
```

---

## 📄 License

MIT © 2025

---

*本项目为电气工程 + AI 交叉领域实践项目，适合大学生科创比赛、课程设计等场景。*
