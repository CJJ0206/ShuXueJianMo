"""V0-1 冷启动输入打包。用法：python coldstart.py <root> [题面文本文件]"""
import sys
from pathlib import Path

BANNER = ("===== 冷启动输入（只允许读这些。读完须复述：每问要算什么 / 现在到哪 / "
          "下一步最该做的三条）=====\n")


def pack(root: Path, problem_text: str = "") -> str:
    """四样输入：题面原文 / SPEC.md / issues.md / 目录树。
    注意：排除规则必须以 root 为基准。曾经按"路径里含 fixtures 就排除"来过滤夹具子目录，
    结果当 root 自身位于 dryrun/fixtures/X 时目录树被打成空的——移交包少一样输入且无人察觉。"""
    root = Path(root)
    skip_parts = {"data", ".git", "__pycache__", "log"}
    tree = "\n".join(sorted(str(p.relative_to(root)).replace("\\", "/")
                            for p in root.rglob("*")
                            if p.is_file()
                            and not (set(p.relative_to(root).parts) & skip_parts)))
    spec = (root / "SPEC.md").read_text(encoding="utf-8") if (root / "SPEC.md").exists() else "（缺）"
    issues = (root / "issues.md").read_text(encoding="utf-8") if (root / "issues.md").exists() else "（缺）"
    n = len([x for x in tree.splitlines() if x.strip()])
    return (f"{BANNER}\n## 题面原文\n{problem_text or '（未提供）'}\n\n"
            f"## SPEC.md\n{spec}\n## issues.md\n{issues}\n"
            f"## 目录树\n（工作区内 {n} 个文件，不含 data/ 与 log/）\n{tree}\n")


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv
    root = Path(argv[1]) if len(argv) > 1 else Path(".")
    text = Path(argv[2]).read_text(encoding="utf-8") if len(argv) > 2 else ""
    out = root / "log" / "coldstart.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    body = pack(root, text)
    out.write_text(body, encoding="utf-8")
    print(f"写 {out}（{len(body)} 字）。喂给一个全新会话，再与 handoff.md 比对；"
          f"命中 <80% 即移交包欠规格，不是新会话笨")
    return 0


if __name__ == "__main__":
    sys.exit(main())
