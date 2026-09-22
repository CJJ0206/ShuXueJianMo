"""V3-1 数字一致性。所有正文数值必须是 numbers.md 里的 N## 引用。
用法：python check_numbers.py <root> [最低链接率=0.95]"""
from __future__ import annotations
import re
import sys
from pathlib import Path

from schema import parse

NUM = re.compile(r"(?<![\w.\-])\d+(?:\.\d+)?%?(?![\w.\-])")
REF = re.compile(r"\[(N\d{2,})\]")
SKIP_LINE = re.compile(r"^\s*(?:[-=]{3,}|\|>|#{1,6}\s|\s*\|)")
# 结构性序号（表3、式(2)、第4问…）不是待溯源数值，从分母里排除而不是记为未链接
STRUCTURAL = re.compile(r"(?:表|图|式|式子|第|章|节|小问|问|页|行|列|参考文献|编号)\s*[（(]?\s*$")


def load_ledger(root: Path) -> dict[str, str]:
    p = Path(root) / "numbers.md"
    return {eid: fields[0] for eid, fields in parse(p)} if p.exists() else {}


def scan(sections: list[Path], ledger: dict[str, str]) -> dict:
    total = linked = 0
    unresolved, dup = [], []
    seen_ids: set[str] = set()
    for p in sections:
        for line in p.read_text(encoding="utf-8").splitlines():
            if SKIP_LINE.match(line):
                continue
            refs = REF.findall(line)
            for eid in refs:
                if eid not in ledger:
                    unresolved.append(eid)
                if eid in seen_ids:
                    dup.append(eid)
                seen_ids.add(eid)
            for m in NUM.finditer(line):
                if STRUCTURAL.search(line[:m.start()]):
                    continue
                total += 1
                if refs:
                    linked += 1
    return dict(total=total, linked=linked,
                unresolved=sorted(set(unresolved)), dup_ids=sorted(set(dup)))


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv
    root = Path(argv[1]) if len(argv) > 1 else Path(".")
    floor = float(argv[2]) if len(argv) > 2 else 0.95
    ledger = load_ledger(root)
    sections = sorted((root / "paper" / "sections").glob("*.md"))
    if not sections:
        print("[V3-1 FAIL] paper/sections/ 下无正文文件")
        return 1
    r = scan(sections, ledger)
    rate = (r["linked"] / r["total"]) if r["total"] else 1.0
    print(f"数值 {r['total']} 处，已链接 {r['linked']} 处，链接率 {rate:.1%}（阈值 {floor:.0%}）")
    if r["unresolved"]:
        print(f"[V3-1 FAIL] 引用了台账不存在的 ID: {r['unresolved']}")
    if r["dup_ids"]:
        print(f"[V3-1 FAIL] 同一 ID 重复出现在多个位置，须核对是否同值: {r['dup_ids']}")
    ok = rate >= floor and not r["unresolved"] and not r["dup_ids"]
    print(f"V3-1 数字一致性: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[V3-1 ERROR] {type(e).__name__}: {e}")
        sys.exit(2)
