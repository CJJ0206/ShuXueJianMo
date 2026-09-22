"""追加一条数值台账。
用法：python numbers_add.py <root> <值> <单位> <来源脚本> <出现位置> <复算方式>"""
import sys
from pathlib import Path

from schema import header, parse


def add(root: Path, value: str, unit: str, source: str, where: str, recompute: str) -> str:
    root = Path(root)
    p = root / "numbers.md"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(header("numbers.md") + "\n", encoding="utf-8")
    fields = [value, unit, source, where, recompute]
    if any(not str(f).strip() for f in fields):
        raise ValueError("numbers 五个字段均不得为空")
    if not (root / source).exists():
        raise ValueError(f"来源脚本不存在: {source}——数字必须可追溯到产生它的脚本")
    eid = f"N{max([int(e[1:]) for e, _ in parse(p)] or [0]) + 1:02d}"
    with p.open("a", encoding="utf-8") as f:
        f.write(eid + "|" + "|".join(fields) + "\n")
    return eid


def main(argv=None) -> int:
    """退出码在 main() 内决定：0 成功、1 违反判据被拒、2 用法错误。
    放在 __main__ 里会让直接调用 main() 的测试绕过异常处理。"""
    argv = argv if argv is not None else sys.argv
    if len(argv) < 7:                      # prog + root + 5 字段
        print(__doc__)
        return 2
    try:
        print("已登记 " + add(Path(argv[1]), *argv[2:7]))
        return 0
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
