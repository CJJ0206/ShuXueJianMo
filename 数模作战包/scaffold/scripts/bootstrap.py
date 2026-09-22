"""生成一题的工作区。用法：python bootstrap.py <root> <小问数>"""
from __future__ import annotations
import argparse
from pathlib import Path

from schema import FACT_FILES, HANDOFF_SECTIONS, header

SPEC_TMPL = "# 本问要算什么 / 交付物是什么 / 对应 SPEC.md 里哪些 C##\n"
VERIFY_TMPL = (
    '"""V2-1 独立复算。禁止 import 本问 src/ 里的任何模块。"""\nimport sys\n\n'
    'GOT = None            # 从 results/ 读求解产物\nEXPECT = None         # 用另一条算法路径重算\n'
    'TOL = 1e-6\nassert GOT is not None and EXPECT is not None, "verify.py 尚未填写"\n'
    'assert abs(GOT - EXPECT) <= TOL * max(1.0, abs(EXPECT)), f"{GOT} != {EXPECT}"\n'
    'print("verify PASS")\nsys.exit(0)\n'
)


def _write(path: Path, text: str, made: list[Path]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    made.append(path)


def build(root: Path, nq: int) -> list[Path]:
    """创建缺失文件，返回新建路径列表。已存在的文件一律不动。"""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    made: list[Path] = []
    for name in FACT_FILES:
        if name == "handoff.md":
            body = "\n".join(f"## {s}\n\n（必填）\n" for s in HANDOFF_SECTIONS)
            _write(root / name, "# 交接备忘。已排除路线一节不得留空。\n" + body + "\n", made)
        else:
            _write(root / name, header(name) + "\n", made)
    for d in ("data/raw", "data/processed", "log"):
        (root / d).mkdir(parents=True, exist_ok=True)
    for sub in ("sections", "figures", "tables"):
        (root / "paper" / sub).mkdir(parents=True, exist_ok=True)
    _write(root / "data" / "REPORT.md",
           "# 附件数据体检报告\n\n## 文件清单\n\n## 结构与类型\n\n## 异常与缺失\n\n## 单位与坐标系\n",
           made)
    _write(root / "tools" / "units.py",
           '"""唯一允许的单位换算处。明天按题面填。"""\n\nMM_PER_PX = None\n', made)
    for i in range(1, nq + 1):
        q = root / f"q{i}"
        _write(q / "spec.md", SPEC_TMPL, made)
        _write(q / "verify.py", VERIFY_TMPL, made)
        (q / "src").mkdir(parents=True, exist_ok=True)
        (q / "results").mkdir(parents=True, exist_ok=True)
    return made


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("nq", type=int)
    args = ap.parse_args()
    created = build(args.root, args.nq)
    print(f"新建 {len(created)} 个文件于 {args.root}")
