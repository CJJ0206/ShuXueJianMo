"""追加一条缺陷登记。
用法：python issue_add.py <root> <定位> <类别> <影响面> <当前假设> <建议验证> <优先级> <复现命令> <owner>"""
import sys
from pathlib import Path

from schema import header, parse


def add(root: Path, loc, kind, impact, assume, verify, pri, repro, owner) -> str:
    root = Path(root)
    p = root / "issues.md"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(header("issues.md") + "\n", encoding="utf-8")
    if not str(repro).strip():
        raise ValueError("缺复现命令，拒绝登记：未登记的瑕疵是事故")
    if not str(owner).strip():
        raise ValueError("缺 owner：一个条目必须只有一个 owner")
    fields = [loc, kind, impact, assume, verify, pri, repro, owner, "open"]
    eid = f"I{max([int(e[1:]) for e, _ in parse(p)] or [0]) + 1:02d}"
    with p.open("a", encoding="utf-8") as f:
        f.write(eid + "|" + "|".join(fields) + "\n")
    return eid


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv
    if len(argv) < 11:
        print(__doc__)
        return 1
    print("已登记 " + add(Path(argv[1]), *argv[2:10]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
