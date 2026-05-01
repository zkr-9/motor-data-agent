"""Agent 工具定义 — 面向 OpenAI Function Calling 的工具集"""

import json
from utils.motor_analysis import (
    load_data, basic_stats, detect_anomalies, comparative_report
)
from visualization.plotter import plot_all

# 全局数据缓存 (避免重复加载)
_data_cache = {"df": None, "path": ""}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "load_motor_data",
            "description": "加载电机实验CSV数据文件。使用其他工具前必须先调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "CSV文件的完整路径，例如 data/motor_data.csv"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_basic_stats",
            "description": "计算电机实验数据的统计量，包括电压/电流/转速/转矩/功率/温度/振动的均值、最值、标准差，以及效率估算。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detect_anomalies",
            "description": "检测电机实验数据中的异常，包括过流(>4.2A)、过热(>80℃)、振动超标(>4.5mm/s)、电压跌落(<360V)、转速骤降(<1430rpm)及故障标签段。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_plots",
            "description": "一键生成全部可视化图表：综合概览图、效率-负载特性曲线、异常检测仪表盘。返回各图表的文件路径。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "full_report",
            "description": "生成完整的电机实验分析报告（文字版），包含电气/机械参数统计和异常检测结果。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


def execute_tool(tool_name: str, arguments: dict) -> str:
    """执行工具并返回 JSON 字符串结果"""

    if tool_name == "load_motor_data":
        filepath = arguments.get("filepath", "")
        try:
            df = load_data(filepath)
            _data_cache["df"] = df
            _data_cache["path"] = filepath
            return json.dumps({
                "ok": True,
                "rows": len(df),
                "columns": list(df.columns),
                "preview": df.head(5).to_dict(orient="records"),
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

    df = _data_cache.get("df")
    if df is None:
        return json.dumps({"ok": False, "error": "请先用 load_motor_data 加载数据"}, ensure_ascii=False)

    if tool_name == "get_basic_stats":
        try:
            stats = basic_stats(df)
            return json.dumps({"ok": True, "stats": stats}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

    elif tool_name == "detect_anomalies":
        try:
            anomalies = detect_anomalies(df)
            return json.dumps({"ok": True, "anomalies": anomalies}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

    elif tool_name == "generate_plots":
        try:
            results = plot_all(df)
            return json.dumps({"ok": True, "plots": results}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

    elif tool_name == "full_report":
        try:
            report = comparative_report(df)
            return json.dumps({"ok": True, "report": report}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

    return json.dumps({"ok": False, "error": f"未知工具: {tool_name}"}, ensure_ascii=False)
