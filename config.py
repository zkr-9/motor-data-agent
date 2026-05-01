"""电机实验数据智能处理与可视化 Agent — 配置模块"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM 配置 ─────────────────────────────────────────────
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY",  "sk-placeholder")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL    = os.getenv("OPENAI_MODEL",    "gpt-4o-mini")

# ── 数据路径 ─────────────────────────────────────────────
DATA_DIR      = os.path.join(os.path.dirname(__file__), "data")
SAMPLE_CSV    = os.path.join(DATA_DIR, "motor_data.csv")
OUTPUT_DIR    = os.path.join(os.path.dirname(__file__), "output")

# ── 可视化默认参数 ───────────────────────────────────────
FIGURE_DPI    = 150
FIGURE_SIZE   = (10, 5)
PLOT_STYLE    = "seaborn-v0_8-darkgrid"

# ── Agent 行为 ───────────────────────────────────────────
MAX_TOOL_CALLS = 8          # 单次对话最多工具调用次数
TEMPERATURE    = 0.3        # LLM 温度
