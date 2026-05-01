"""电机实验数据可视化 — matplotlib 专业绘图"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # 非交互后端, 服务器/CLI 兼容
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import config

# 全局样式设置
plt.rcParams["figure.dpi"]     = config.FIGURE_DPI
plt.rcParams["savefig.dpi"]    = config.FIGURE_DPI
plt.rcParams["font.family"]    = "sans-serif"
plt.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

# 统一配色
COLORS = {
    "voltage":    "#E74C3C",
    "current":    "#3498DB",
    "speed":      "#2ECC71",
    "torque":     "#F39C12",
    "power":      "#9B59B6",
    "temperature":"#E67E22",
    "vibration":  "#1ABC9C",
    "efficiency": "#2980B9",
    "normal":     "#2ECC71",
    "warning":    "#F39C12",
    "danger":     "#E74C3C",
}

os.makedirs(config.OUTPUT_DIR, exist_ok=True)


def _save_and_return(fig, filename: str) -> str:
    """保存图片并返回路径"""
    path = os.path.join(config.OUTPUT_DIR, filename)
    fig.savefig(path, bbox_inches="tight", dpi=config.FIGURE_DPI)
    plt.close(fig)
    return path


def plot_overview(df: pd.DataFrame) -> str:
    """综合概览图 — 电气+机械参数子图矩阵 (3×2)"""
    fig, axes = plt.subplots(3, 2, figsize=(14, 10))
    t = df["time_s"].values

    panels = [
        (0, 0, "voltage_V",     "电压 / V",      COLORS["voltage"]),
        (0, 1, "current_A",     "电流 / A",      COLORS["current"]),
        (1, 0, "speed_rpm",     "转速 / rpm",    COLORS["speed"]),
        (1, 1, "torque_Nm",     "转矩 / N·m",    COLORS["torque"]),
        (2, 0, "temperature_C", "绕组温度 / ℃",  COLORS["temperature"]),
        (2, 1, "vibration_mm_s","振动 / mm/s",   COLORS["vibration"]),
    ]

    for r, c, col, ylabel, color in panels:
        ax = axes[r][c]
        ax.plot(t, df[col].values, color=color, linewidth=0.8, alpha=0.9)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_xlabel("时间 / s", fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.tick_params(labelsize=8)

    # 故障区域高亮
    if "fault_flag" in df.columns:
        for r in range(3):
            for c_idx in range(2):
                _highlight_faults(axes[r][c_idx], df)

    fig.suptitle("三相异步电机实验 — 综合数据概览", fontsize=14, fontweight="bold", y=1.01)
    fig.tight_layout()
    return _save_and_return(fig, "00_overview.png")


def plot_efficiency_curve(df: pd.DataFrame) -> str:
    """效率-负载特性曲线（电机学经典图）"""
    if not {"torque_Nm", "speed_rpm", "power_W"}.issubset(df.columns):
        return ""

    p_out = df["torque_Nm"] * df["speed_rpm"] * np.pi / 30
    p_in  = df["power_W"]
    eff   = np.clip(p_out / p_in, 0, 1) * 100
    load  = df["torque_Nm"] / df["torque_Nm"].max()

    fig, ax1 = plt.subplots(figsize=config.FIGURE_SIZE)

    ax1.scatter(load, eff, c=COLORS["efficiency"], s=12, alpha=0.6, label="效率")
    ax1.set_xlabel("负载率 (T/T_max)", fontsize=11)
    ax1.set_ylabel("效率 / %", fontsize=11, color=COLORS["efficiency"])
    ax1.tick_params(axis="y", labelcolor=COLORS["efficiency"])
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.scatter(load, df["temperature_C"], c=COLORS["temperature"], s=8, alpha=0.4, label="温度")
    ax2.set_ylabel("绕组温度 / ℃", fontsize=11, color=COLORS["temperature"])
    ax2.tick_params(axis="y", labelcolor=COLORS["temperature"])

    # 标出最高效率点
    best_idx = eff.idxmax()
    ax1.annotate(f"最高效率 {eff[best_idx]:.1f}%",
                 xy=(load[best_idx], eff[best_idx]),
                 xytext=(load[best_idx]+0.1, eff[best_idx]-5),
                 arrowprops=dict(arrowstyle="->", color="red"),
                 fontsize=9, color="red")

    fig.suptitle("电机效率-负载特性曲线", fontsize=13, fontweight="bold")
    fig.tight_layout()
    return _save_and_return(fig, "01_efficiency_curve.png")


def plot_anomaly_dashboard(df: pd.DataFrame) -> str:
    """异常检测仪表盘 — 故障时段 + 振动谱"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    t = df["time_s"].values

    # ── 左上: 电流+过流阈值 ──
    ax = axes[0][0]
    ax.plot(t, df["current_A"], color=COLORS["current"], linewidth=0.8)
    ax.axhline(y=4.2, color="red", linestyle="--", linewidth=1, label="过流阈值 4.2A")
    ax.set_ylabel("电流 / A")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    _highlight_faults(ax, df)

    # ── 右上: 温度+过热阈值 ──
    ax = axes[0][1]
    ax.plot(t, df["temperature_C"], color=COLORS["temperature"], linewidth=0.8)
    ax.axhline(y=80, color="red", linestyle="--", linewidth=1, label="过热阈值 80℃")
    ax.set_ylabel("温度 / ℃")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    _highlight_faults(ax, df)

    # ── 左下: 振动+超标阈值 ──
    ax = axes[1][0]
    ax.plot(t, df["vibration_mm_s"], color=COLORS["vibration"], linewidth=0.8)
    ax.axhline(y=4.5, color="red", linestyle="--", linewidth=1, label="振动阈值 4.5mm/s")
    ax.set_ylabel("振动 / mm/s")
    ax.set_xlabel("时间 / s")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    _highlight_faults(ax, df)

    # ── 右下: 故障标记 ──
    ax = axes[1][1]
    if "fault_flag" in df.columns:
        colors = ["green", "orange", "red"]
        labels = ["正常", "轻微异常", "严重异常"]
        for level in [0, 1, 2]:
            mask = df["fault_flag"] == level
            if mask.sum() > 0:
                ax.scatter(t[mask], df["speed_rpm"][mask],
                           c=colors[level], s=8, alpha=0.6, label=labels[level])
    ax.set_ylabel("转速 / rpm")
    ax.set_xlabel("时间 / s")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.suptitle("电机异常检测仪表盘", fontsize=13, fontweight="bold")
    fig.tight_layout()
    return _save_and_return(fig, "02_anomaly_dashboard.png")


def _highlight_faults(ax, df: pd.DataFrame):
    """在图上高亮故障区域"""
    if "fault_flag" not in df.columns:
        return
    fault_mask = df["fault_flag"] > 0
    if fault_mask.sum() == 0:
        return
    ymin, ymax = ax.get_ylim()
    in_segment = False
    start_t = 0
    for i in range(len(df)):
        if fault_mask.iloc[i] and not in_segment:
            start_t = df["time_s"].iloc[i]
            in_segment = True
        elif not fault_mask.iloc[i] and in_segment:
            ax.axvspan(start_t, df["time_s"].iloc[i - 1],
                       alpha=0.12, color="red")
            in_segment = False
    if in_segment:
        ax.axvspan(start_t, df["time_s"].iloc[-1],
                   alpha=0.12, color="red")
    ax.set_ylim(ymin, ymax)


def plot_all(df: pd.DataFrame) -> dict:
    """一键生成全部图表, 返回 {图表名: 文件路径}"""
    results = {}
    try:
        results["overview"] = plot_overview(df)
    except Exception as e:
        results["overview"] = f"❌ {e}"
    try:
        results["efficiency_curve"] = plot_efficiency_curve(df)
    except Exception as e:
        results["efficiency_curve"] = f"❌ {e}"
    try:
        results["anomaly_dashboard"] = plot_anomaly_dashboard(df)
    except Exception as e:
        results["anomaly_dashboard"] = f"❌ {e}"
    return results
