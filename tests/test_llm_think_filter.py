"""思考链剥离：推理模型把 <think>…</think> 内联进 content 时不该漏给孩子。

用法：python tests/test_llm_think_filter.py

为什么单独一组：标签完全可能被切在两个流式分片之间（"<thi" + "nk>…"、
"…</thi" + "nk>"），逐片 replace 会漏掉半截标签，屏幕上就会冒出
"<think>用户要求我作为…" 这种半截话。所以这里逐个位置都试过。
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PANDA_DATA_DIR", tempfile.mkdtemp(prefix="panda_think_"))

from server.llm import ThinkFilter, strip_think  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = "") -> None:
    RESULTS.append((name, ok, note))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {note}")


def run_stream(chunks: list[str]) -> str:
    """按分片喂一遍，返回孩子最终看到的文本。"""
    f = ThinkFilter()
    out = "".join(f.feed(c) for c in chunks)
    return out + f.flush()


def split_every(text: str, n: int) -> list[str]:
    return [text[i:i + n] for i in range(0, len(text), n)]


def main() -> int:
    # ---------- 非流式 ----------
    record("整段删除",
           strip_think("<think>用户要求我作为小豆的成长管家</think>今天周六。") == "今天周六。")
    record("没有思考链时原样返回",
           strip_think("今天周六，机器人课 9:30。") == "今天周六，机器人课 9:30。")
    record("多个思考块",
           strip_think("<think>a</think>前<think>b</think>后") == "前后")
    record("跨行思考块",
           strip_think("<think>第一行\n第二行\n第三行</think>正文") == "正文")
    record("被截断的思考块（没闭合）不留残渣",
           strip_think("<think>模型正在想…还没说完就断了") == "")
    record("空串与 None 安全",
           strip_think("") == "" and strip_think(None) == "")

    # ---------- 流式：逐字符切（最狠的情况）----------
    sample = "<think>Let me think about what to say.</think>早上好，今天周六。"
    record("逐字符切分不漏半个标签", run_stream(split_every(sample, 1)) == "早上好，今天周六。")

    # ---------- 流式：各种切口 ----------
    for cut in range(1, len("<think>")):
        a, b = sample[:cut], sample[cut:]
        record(f"开标签被切成 {cut}+{len(b)-cut}", run_stream([a, b]) == "早上好，今天周六。")
    mid = sample.index("</think>")
    for cut in range(mid + 1, mid + 1 + len("</think>")):
        a, b = sample[:cut], sample[cut:]
        record(f"闭标签被切成 {cut}+{len(b)-cut}", run_stream([a, b]) == "早上好，今天周六。")

    # ---------- 流式：真实形状 ----------
    record("思考在前、正文在多个分片",
           run_stream(["<think>用户要求我", "作为小豆的管家", "</think>", "嗯，", "在的。"])
           == "嗯，在的。")
    record("整条流只有思考链时正文为空",
           run_stream(["<think>", "想了好久", "</think>"]) == "")
    record("思考链没闭合也不漏出来",
           run_stream(["<think>想到一半", "被 max_tokens 砍断了"]) == "")
    record("正文里恰好有 think 五个字母不该被误伤",
           run_stream(["我 think", " 过了", "</think> 不存在的标签"]) == "我 think 过了</think> 不存在的标签")
    record("大小写混写的标签",
           run_stream(["<THINK>想</THINK>", "正文"]) == "正文")
    record("思考块后紧跟换行不吞掉正文",
           run_stream(["<think>x</think>\n\n今天记得吃药。"]) == "今天记得吃药。")
    record("连续两次 feed 空串不炸",
           run_stream(["", "正文", ""]) == "正文")

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} 通过")
    for name, ok, note in RESULTS:
        if not ok:
            print(f"  失败：{name}  {note}")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
