"""V0-3 一键复现：依次跑 q*/src/main.py 再跑 q*/verify.py。
用法：python run_all.py <root>"""
import subprocess
import sys
from pathlib import Path


def run(root: Path) -> list[tuple[str, int]]:
    root = Path(root)
    out: list[tuple[str, int]] = []
    for q in sorted(p for p in root.glob("q*") if p.is_dir()):
        for script in (q / "src" / "main.py", q / "verify.py"):
            if not script.exists():
                out.append((f"{q.name}/{script.name} 不存在", 1))
                continue
            r = subprocess.run([sys.executable, str(script)], cwd=q,
                               capture_output=True, text=True, timeout=1800)
            out.append((f"{q.name}/{script.name}", r.returncode))
            if r.returncode:
                print(r.stdout[-1500:], r.stderr[-1500:])
    return out


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv
    res = run(Path(argv[1]) if len(argv) > 1 else Path("."))
    for name, code in res:
        print(f"{'OK  ' if code == 0 else 'FAIL'} {name} (exit {code})")
    bad = [n for n, c in res if c != 0]
    print(f"V0-3 一键复现: {'PASS' if not bad else f'FAIL {len(bad)} 项'}")
    return 0 if not bad else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        sys.exit(2)
