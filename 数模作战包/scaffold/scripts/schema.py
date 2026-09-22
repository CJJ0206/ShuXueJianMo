"""六份事实源的行格式契约。改协议只改这一个文件。"""
from __future__ import annotations
import re
from pathlib import Path

SCHEMAS = {
    "SPEC.md":        dict(prefix="C", fields=["原文引用", "解读", "软硬", "单位", "验收断言", "所属小问"]),
    "assumptions.md": dict(prefix="A", fields=["内容", "理由", "影响面", "验证方式", "若为假后果"]),
    "numbers.md":     dict(prefix="N", fields=["值", "单位", "来源脚本", "出现位置", "复算方式"]),
    "decisions.md":   dict(prefix="D", fields=["决策", "备选", "理由", "放弃代价", "时间"]),
    "issues.md":      dict(prefix="I", fields=["定位", "类别", "影响面", "当前假设", "建议验证",
                                               "优先级", "复现命令", "owner", "状态"]),
}
FACT_FILES = ("SPEC.md", "assumptions.md", "numbers.md", "decisions.md", "issues.md", "handoff.md")
HANDOFF_SECTIONS = ["当前状态", "已排除路线及原因", "最可疑三处", "下一步三条"]
ID_RE = re.compile(r"^([A-Z])(\d{2,})\|(.*)$")
# 字段内出现竖线是常态（表头名、区间、公式），故约定用 \| 转义，切分时只在未转义的竖线处切。
UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")


def split_fields(rest: str) -> list[str]:
    return [f.strip().replace("\\|", "|") for f in UNESCAPED_PIPE.split(rest)]


def parse(path: Path) -> list[tuple[str, list[str]]]:
    """跳过 # 注释与空行，返回 [(ID, [字段...])]。格式不符抛 ValueError。"""
    out = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = ID_RE.match(line)
        if not m:
            raise ValueError(f"{path.name}:{lineno} 不是合法条目行: {raw[:40]}")
        prefix, num, rest = m.groups()
        schema = SCHEMAS[path.name]
        if prefix != schema["prefix"]:
            raise ValueError(f"{path.name}:{lineno} ID 前缀应为 {schema['prefix']}，实为 {prefix}")
        fields = split_fields(rest)
        want = len(schema["fields"])
        if len(fields) != want:
            raise ValueError(f"{path.name}:{lineno} 需 {want} 字段，实为 {len(fields)}"
                             f"（字段内含竖线须写成反斜杠转义）")
        out.append((f"{prefix}{num}", fields))
    return out


def header(name: str) -> str:
    return "# id|" + "|".join(SCHEMAS[name]["fields"])
