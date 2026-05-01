#!/usr/bin/env python3
"""
电机实验数据智能处理与可视化 AI Agent — 主程序入口
=====================================================
用法:
    python main.py                     # 交互对话模式
    python main.py --generate-data     # 生成样本数据
    python main.py --quick             # 一键分析+出图(自动模式)

电气工程 | 三相异步电机 | AI Agent
"""

import sys
import os
import argparse

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import MotorExperimentAgent
from data.sample_generator import save_sample_data
import config


BANNER = r"""
╔══════════════════════════════════════════════════════════╗
║     ⚡ 电机实验数据智能处理与可视化 AI Agent ⚡          ║
║     Motor Experiment Data AI Agent v1.0                  ║
║     三相异步电机 | 电气工程 | 智能诊断                   ║
╚══════════════════════════════════════════════════════════╝
"""


def generate_sample():
    """生成样本电机实验数据"""
    print("📊 正在生成仿真的三相异步电机实验数据...")
    df = save_sample_data(config.SAMPLE_CSV, num_points=200)
    print(f"✅ 已生成 {len(df)} 行 × {len(df.columns)} 列 数据")
    print(f"   保存位置: {config.SAMPLE_CSV}")
    print(f"\n数据预览:")
    print(df.head(8).to_string())


def quick_analysis():
    """一键分析模式：生成样本 → 加载 → 分析 → 出图"""
    print(BANNER)
    print("⚡ 一键自动分析模式\n")

    # 1. 生成样本
    if not os.path.exists(config.SAMPLE_CSV):
        print("[1/4] 生成样本数据...")
        save_sample_data(config.SAMPLE_CSV, num_points=200)
    else:
        print("[1/4] 样本数据已存在，跳过生成")

    # 2. 创建 Agent 并自动分析
    print("[2/4] 初始化 AI Agent...")
    agent = MotorExperimentAgent()

    print("[3/4] AI Agent 分析中...\n")
    response = agent.chat(
        f"请加载 {config.SAMPLE_CSV} 数据文件，"
        "然后依次帮我做三件事："
        "1) 查看基本统计信息；"
        "2) 检测所有异常；"
        "3) 生成全部可视化图表。"
        "最后用中文给出专业结论和建议。"
    )
    print(f"\n📝 Agent 回复:\n{response}")

    print(f"\n[4/4] 图表已生成至: {config.OUTPUT_DIR}/")
    if os.path.exists(config.OUTPUT_DIR):
        for f in sorted(os.listdir(config.OUTPUT_DIR)):
            print(f"  📈 {f}")


def interactive_mode():
    """交互对话模式"""
    print(BANNER)
    print("💬 交互对话模式 (输入 'quit' 退出, 'reset' 重置对话)\n")

    # 检查并生成数据
    if not os.path.exists(config.SAMPLE_CSV):
        print("⚠ 未找到样本数据，正在自动生成...")
        save_sample_data(config.SAMPLE_CSV, num_points=200)
        print(f"✅ 样本数据: {config.SAMPLE_CSV}\n")

    agent = MotorExperimentAgent()

    print(f"📂 数据路径: {config.SAMPLE_CSV}")
    print(f"🤖 模型: {config.OPENAI_MODEL}")
    print(f"📊 输出目录: {config.OUTPUT_DIR}/")
    print()
    print("你可以尝试:")
    print('  • "帮我加载数据并分析有没有异常"')
    print('  • "画一个效率-负载曲线"')
    print('  • "生成完整分析报告"')
    print('  • "这批数据整体质量如何？"\n')

    while True:
        try:
            user_input = input("👤 你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("👋 再见!")
            break
        if user_input.lower() in ("reset", "clear"):
            agent.reset()
            print("🔄 对话已重置")
            continue

        print()
        response = agent.chat(user_input)
        print(f"\n🤖 Agent: {response}\n")


def main():
    parser = argparse.ArgumentParser(
        description="电机实验数据智能处理与可视化 AI Agent"
    )
    parser.add_argument(
        "--generate-data", "-g",
        action="store_true",
        help="生成仿真样本电机实验数据"
    )
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="一键自动分析模式：生成数据→加载→分析→出图"
    )
    args = parser.parse_args()

    if args.generate_data:
        generate_sample()
    elif args.quick:
        quick_analysis()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
