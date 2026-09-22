"""V0-3 一键复现：依次跑 q*/src/main.py 再跑 q*/verify.py。
用法：python run_all.py <root>

中文 Windows 上 subprocess 的 text=True 会按 GBK 解码，子进程一打中文就崩
（reader 线程抛 UnicodeDecodeError，stdout 变成 None）。故必须显式 encoding=utf-8，
并对 None 兜底。"""
import subprocess
import sys
from pathlib import Path

ENC = dict(text=True, encoding="utf-8", errors="replace")


def run(root: Path) -> list[tuple[str, int]]:
    root = Path(root)
    out: list[tuple[str, int]] = []
    for q in sorted(p for p in root.glob("q*") if p.is_dir()):
        for script in (q / "src" / "main.py", q / "verify.py"):
            if not script.exists():
                out.append((f"{q.name}/{script.name} 不存在", 1))
                continue
            try:
                r = subprocess.run([sys.executable, str(script)], cwd=q,
                                   capture_output=True, timeout=1800, **ENC)
                code, so, se = r.returncode, r.stdout, r.stderr
            except subprocess.TimeoutExpired as e:
                code, so, se = 124, e.stdout, e.stderr
            out.append((f"{q.name}/{script.name}", code))
            if code:
                print((so or "")[-1500:], (se or "")[-1500:])
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
