"""V2-6 环境快照。用法：python env_lock.py <root> → 写 <root>/env.lock"""
import platform
import subprocess
import sys
from pathlib import Path


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv
    root = Path(argv[1]) if len(argv) > 1 else Path(".")
    try:
        import torch
        cuda = torch.cuda.is_available()
        gputxt = torch.cuda.get_device_name(0) if cuda else "NO CUDA"
        tver = torch.__version__
    except Exception as e:
        gputxt, tver = f"torch 不可用: {e}", "?"
    proc = subprocess.run([sys.executable, "-m", "pip", "freeze"],
                          capture_output=True, text=True)
    npk = proc.stdout.count("\n")
    lines = [f"python {sys.version.split()[0]} ({sys.executable})",
             platform.platform(),
             f"torch {tver}; GPU: {gputxt}",
             f"pip freeze 包数 {npk}",
             "seed 约定：所有随机实验必须显式 seed=42 并在 spec.md 里记"]
    root.mkdir(parents=True, exist_ok=True)
    (root / "env.lock").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"写 {root / 'env.lock'}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        sys.exit(2)
