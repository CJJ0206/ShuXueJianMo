"""V1 结构验收。用法：python check_structure.py <root>  退出码 0=通过 1=不通过 2=异常"""
from __future__ import annotations
import re
import sys
from pathlib import Path

from schema import FACT_FILES, parse

PLACEHOLDER = re.compile(r"TODO|TBD|FIXME|待补|占位|XXX|此处填写")


def _md_files(root: Path):
    for p in sorted(root.rglob("*.md")):
        if "fixtures" in p.parts or "data\\raw" in str(p) or "data/raw" in str(p).replace("\\", "/"):
            continue
        yield p


def _check_placeholders(root: Path) -> list[str]:
    out = []
    for p in _md_files(root):
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if PLACEHOLDER.search(line) and "禁止" not in line and "占位符" not in line:
                out.append(f"占位符 {p.relative_to(root)}:{i}: {line.strip()[:60]}")
    return out


def _check_empty_sections(root: Path) -> list[str]:
    out = []
    for p in _md_files(root):
        lines = p.read_text(encoding="utf-8").splitlines()
        heads = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
        for k, i in enumerate(heads):
            end = heads[k + 1] if k + 1 < len(heads) else len(lines)
            body = [ln for ln in lines[i + 1:end] if ln.strip() and not ln.startswith("#")]
            if not body:
                out.append(f"空章节 {p.relative_to(root)}:{i+1}: {lines[i].strip()[:40]}")
    return out


def _check_fact_files(root: Path) -> list[str]:
    out = []
    for name in FACT_FILES:
        p = root / name
        if not p.exists():
            out.append(f"缺文件 {name}")
            continue
        text = p.read_text(encoding="utf-8")
        if name == "handoff.md":
            if "（必填）" in text:
                out.append("handoff.md 仍有未填的小节")
            if len(text.strip().splitlines()) < 6:
                out.append("handoff.md 过短")
            continue
        try:
            entries = parse(p)
        except ValueError as e:
            out.append(f"{name} 行格式: {e}")
            continue
        if name == "SPEC.md" and not entries:
            out.append("SPEC.md 无任何约束条目——说明题面解析没跑")
        for eid, fields in entries:
            if name == "numbers.md" and fields[2] and fields[2] != "-":
                if not (root / fields[2]).exists():
                    out.append(f"{name} {eid} 来源脚本不存在: {fields[2]}")
            if name == "issues.md":
                if not fields[6].strip():
                    out.append(f"{name} {eid} 缺复现命令")
                if not fields[7].strip():
                    out.append(f"{name} {eid} 缺 owner")
    return out


def _check_questions(root: Path) -> list[str]:
    out = []
    qs = sorted(p for p in root.glob("q*") if re.fullmatch(r"q\d+", p.name))
    for q in qs:
        for need in ("spec.md", "verify.py"):
            if not (q / need).exists():
                out.append(f"缺 {q.name}/{need}")
        for d in ("src", "results"):
            if not (q / d).is_dir():
                out.append(f"缺目录 {q.name}/{d}")
    if not qs:
        out.append("没有任何 q*/ 小问目录")
    return out


def check(root: Path) -> list[str]:
    root = Path(root)
    return (_check_fact_files(root) + _check_questions(root)
            + _check_placeholders(root) + _check_empty_sections(root))


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv
    root = Path(argv[1]) if len(argv) > 1 else Path(".")
    problems = check(root)
    for p in problems:
        print(f"[V1 FAIL] {p}")
    print(f"V1 结构验收: {'PASS' if not problems else f'FAIL（{len(problems)} 项）'}  root={root}")
    return 0 if not problems else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[V1 ERROR] {type(e).__name__}: {e}")
        sys.exit(2)
