"""生成仿真的三相异步电机实验数据，贴近真实实验场景"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)


def generate_motor_data(num_points: int = 200) -> pd.DataFrame:
    """
    生成电机实验数据，包含以下字段:
      - time(s)       : 采样时间
      - voltage(V)    : 三相平均线电压 (380V ±2%)
      - current(A)    : 定子电流 (空载→满载 0.8A→4.2A)
      - speed(rpm)    : 转速 (空载 1498→满载 1440 rpm)
      - torque(N·m)   : 电磁转矩
      - power(W)      : 输入功率
      - temperature(℃): 绕组温度
      - vibration(mm/s): 振动烈度
      - fault_flag    : 故障标记 (0=正常, 1=轻微异常, 2=严重异常)
    """

    t = np.linspace(0, 200, num_points)

    # ── 负载从空载渐变到额定，再回到轻载（模拟完整实验流程）──
    load_factor = (
        0.1 + 0.7 * np.sin(np.pi * t / 200) ** 2
        + 0.05 * np.random.randn(num_points)
    )
    load_factor = np.clip(load_factor, 0.05, 1.0)

    # 电压 — 三相平均，380V ±2% 波动
    voltage = 380 + 2.5 * np.sin(0.3 * t) + 1.5 * np.random.randn(num_points)

    # 电流 — 随负载增大，基值 0.8A → 4.5A
    current = 0.8 + 3.7 * load_factor + 0.08 * np.random.randn(num_points)
    current = np.clip(current, 0.5, 5.0)

    # 转速 — 异步电机转差率约 0.1%→4%
    sync_speed = 1500
    slip = 0.001 + 0.039 * load_factor + 0.002 * np.random.randn(num_points)
    speed = sync_speed * (1 - slip) + 0.5 * np.random.randn(num_points)

    # 转矩 — τ ∝ P / ω
    torque = (current * voltage * 0.82) / (speed * np.pi / 30) * 0.85
    torque += 0.02 * np.random.randn(num_points)
    torque = np.clip(torque, 0.05, 5.0)

    # 功率 — P = √3·U·I·cosφ
    pf = 0.78 + 0.1 * load_factor + 0.02 * np.random.randn(num_points)
    pf = np.clip(pf, 0.7, 0.92)
    power = np.sqrt(3) * voltage * current * pf

    # 温度 — 绕组温度逐渐上升 (环境25℃ → 稳态~75℃)
    ambient = 25
    temp_rise = 50 * (1 - np.exp(-t / 60)) * (0.7 + 0.3 * load_factor)
    temperature = ambient + temp_rise + 0.8 * np.random.randn(num_points)

    # 振动 — 正常 <2.8 mm/s, 异常 >4.5 mm/s
    vibration_base = 1.2 + 1.6 * load_factor + 0.15 * np.random.randn(num_points)

    # ── 故障标记: 模拟局部短路 / 轴承磨损 ──
    fault_flag = np.zeros(num_points, dtype=int)
    # 区域1: 轻微异常 (t 80~120, 轴承早期)
    mask1 = (t > 80) & (t <= 120)
    fault_flag[mask1] = np.random.choice([0, 1], size=mask1.sum(), p=[0.3, 0.7])
    vibration_base[mask1] += 1.8 * (fault_flag[mask1] == 1)

    # 区域2: 严重异常 (t > 160, 匝间短路)
    mask2 = t > 160
    fault_flag[mask2] = np.random.choice([1, 2], size=mask2.sum(), p=[0.3, 0.7])
    vibration_base[mask2] += 3.5 * (fault_flag[mask2] == 2)
    current[mask2] += 1.2 * (fault_flag[mask2] == 2)
    temperature[mask2] += 8.0 * (fault_flag[mask2] == 2)

    vibration = np.clip(vibration_base, 0.5, 10.0)

    df = pd.DataFrame({
        "time_s":         np.round(t, 1),
        "voltage_V":      np.round(voltage, 1),
        "current_A":      np.round(current, 3),
        "speed_rpm":      np.round(speed, 1),
        "torque_Nm":      np.round(torque, 3),
        "power_W":        np.round(power, 1),
        "temperature_C":  np.round(temperature, 1),
        "vibration_mm_s": np.round(vibration, 3),
        "fault_flag":     fault_flag,
    })

    return df


def save_sample_data(filepath: str, num_points: int = 200):
    """生成并保存样本数据"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df = generate_motor_data(num_points)
    df.to_csv(filepath, index=False, encoding="utf-8")
    return df


if __name__ == "__main__":
    import config
    df = save_sample_data(config.SAMPLE_CSV, 200)
    print(f"✅ 样本数据已生成: {config.SAMPLE_CSV}")
    print(f"   行数: {len(df)}, 列数: {len(df.columns)}")
    print(df.head())
