"""电机实验数据核心分析工具 — 贴近电气工程专业课内容"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple


def load_data(filepath: str) -> pd.DataFrame:
    """加载电机实验数据"""
    return pd.read_csv(filepath)


def basic_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """计算关键参数的统计量（均值/最值/标准差）"""
    cols = ["voltage_V", "current_A", "speed_rpm",
            "torque_Nm", "power_W", "temperature_C", "vibration_mm_s"]
    stats = {}
    for c in cols:
        if c in df.columns:
            stats[c] = {
                "mean": round(float(df[c].mean()), 3),
                "max":  round(float(df[c].max()), 3),
                "min":  round(float(df[c].min()), 3),
                "std":  round(float(df[c].std()), 3),
            }
    # 效率估算
    if "torque_Nm" in df.columns and "speed_rpm" in df.columns and "power_W" in df.columns:
        p_out = df["torque_Nm"] * df["speed_rpm"] * np.pi / 30
        p_in  = df["power_W"]
        efficiency = np.clip(p_out / p_in, 0, 1)
        stats["efficiency"] = {
            "mean": round(float(efficiency.mean()) * 100, 1),
            "max":  round(float(efficiency.max()) * 100, 1),
            "min":  round(float(efficiency.min()) * 100, 1),
        }
    return stats


def efficiency_curve(df: pd.DataFrame) -> pd.DataFrame:
    """计算效率随负载变化曲线"""
    if not {"torque_Nm", "speed_rpm", "power_W"}.issubset(df.columns):
        return pd.DataFrame()
    p_out = df["torque_Nm"] * df["speed_rpm"] * np.pi / 30
    p_in  = df["power_W"]
    eff   = np.clip(p_out / p_in, 0, 1) * 100
    result = df[["time_s", "torque_Nm", "speed_rpm"]].copy()
    result["efficiency_%"] = eff.round(1)
    result["load_ratio"]   = (df["torque_Nm"] / df["torque_Nm"].max()).round(3)
    return result


def detect_anomalies(df: pd.DataFrame) -> Dict[str, Any]:
    """基于规则的异常检测（电气专业常用判据）"""
    anomalies = {
        "overcurrent": [],       # 过流 >4.2A
        "overheat": [],          # 过热 >80℃
        "high_vibration": [],    # 振动超标 >4.5 mm/s
        "voltage_drop": [],      # 电压跌落 <360V
        "speed_drop": [],        # 转速骤降 <1430 rpm
        "fault_segments": [],    # 故障标签段
    }

    for i, row in df.iterrows():
        t = row["time_s"]
        if row["current_A"] > 4.2:
            anomalies["overcurrent"].append(f"t={t:.0f}s I={row['current_A']:.2f}A")
        if row["temperature_C"] > 80:
            anomalies["overheat"].append(f"t={t:.0f}s T={row['temperature_C']:.1f}℃")
        if row["vibration_mm_s"] > 4.5:
            anomalies["high_vibration"].append(f"t={t:.0f}s Vib={row['vibration_mm_s']:.2f}mm/s")
        if row["voltage_V"] < 360:
            anomalies["voltage_drop"].append(f"t={t:.0f}s U={row['voltage_V']:.1f}V")
        if row["speed_rpm"] < 1430:
            anomalies["speed_drop"].append(f"t={t:.0f}s n={row['speed_rpm']:.0f}rpm")

    # 故障标签段汇总
    if "fault_flag" in df.columns:
        fault_df = df[df["fault_flag"] > 0]
        if len(fault_df) > 0:
            segs = []
            start = fault_df["time_s"].iloc[0]
            prev  = start
            for t in fault_df["time_s"].iloc[1:]:
                if t - prev > 2:
                    segs.append(f"{start:.0f}s→{prev:.0f}s")
                    start = t
                prev = t
            segs.append(f"{start:.0f}s→{prev:.0f}s")
            anomalies["fault_segments"] = segs

    return anomalies


def comparative_report(df: pd.DataFrame) -> str:
    """生成电机实验可读分析报告"""
    stats = basic_stats(df)
    anomalies = detect_anomalies(df)

    lines = []
    lines.append("=" * 60)
    lines.append("          三相异步电机实验数据分析报告")
    lines.append("=" * 60)

    lines.append(f"\n📊 数据概况: {len(df)} 个采样点, {len(df.columns)} 个通道")

    lines.append("\n── 电气参数 ──")
    for k in ["voltage_V", "current_A", "power_W"]:
        if k in stats:
            s = stats[k]
            lines.append(f"  {k}: 均值={s['mean']}  范围=[{s['min']}, {s['max']}]  σ={s['std']}")

    lines.append("\n── 机械参数 ──")
    for k in ["speed_rpm", "torque_Nm", "vibration_mm_s"]:
        if k in stats:
            s = stats[k]
            lines.append(f"  {k}: 均值={s['mean']}  范围=[{s['min']}, {s['max']}]  σ={s['std']}")

    if "efficiency" in stats:
        e = stats["efficiency"]
        lines.append(f"\n⚡ 效率: 平均={e['mean']}%  最高={e['max']}%  最低={e['min']}%")

    lines.append("\n── 异常检测 ──")
    for k, v in anomalies.items():
        label = {
            "overcurrent": "过流", "overheat": "过热",
            "high_vibration": "振动超标", "voltage_drop": "电压跌落",
            "speed_drop": "转速骤降", "fault_segments": "故障时段"
        }.get(k, k)
        if v:
            lines.append(f"  ⚠ {label}: {len(v)} 处")
            for item in v[:5]:
                lines.append(f"      {item}")
        else:
            lines.append(f"  ✅ {label}: 未检出")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)
