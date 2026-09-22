"""卡片完整性计数器。用法：python count_cards.py <文件或目录> [期望张数]
判据：每个 ### 卡 块必须含七个字段标签，验证状态取值合法。"""
import re
import sys
from pathlib import Path

FIELDS = ["触发时机", "输入", "prompt", "必落文件", "30 秒人工判定", "已知失效模式", "验证状态"]
STATUS = re.compile(r"未压测|已压测@|已修订@")


def files_of(target: str):
    p = Path(target)
    return [p] if p.is_file() else sorted(p.glob("*.md"))


def count(target: str):
    total, bad, per_file = 0, [], {}
    for f in files_of(target):
        blocks = re.split(r"^### 卡 ", f.read_text(encoding="utf-8"), flags=re.M)[1:]
        per_file[f.name] = len(blocks)
        for b in blocks:
            total += 1
            name = b.splitlines()[0].strip()
            missing = [x for x in FIELDS if f"**{x}" not in b]
            if missing:
                bad.append(f"{name}: 缺字段 {missing}")
            if not STATUS.search(b):
                bad.append(f"{name}: 验证状态取值非法（须为 未压测 / 已压测@X / 已修订@X）")
            if "```text" not in b and "```" not in b:
                bad.append(f"{name}: 缺 prompt 代码块")
    return total, bad, per_file


def main(argv):
    target = argv[1] if len(argv) > 1 else "prompts"
    want = int(argv[2]) if len(argv) > 2 else None
    total, bad, per_file = count(target)
    for k, v in sorted(per_file.items()):
        print(f"  {k}: {v} 张")
    print(f"卡片总数 {total}" + (f"（期望 {want}）" if want is not None else ""))
    for x in bad:
        print("[FAIL]", x)
    ok = not bad and (want is None or total == want)
    print("PASS" if ok else f"FAIL {len(bad)} 项" + ("" if not bad or want is None or total == want
                                                    else " + 张数不符"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
