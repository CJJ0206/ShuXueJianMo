# 数模参赛作战包 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建成一套与具体赛题无关的数学建模参赛作战包（执行规范 + 验收规范 + 30 张 prompt 卡 + 工程脚手架），并用本地两套夹具把它压测到能上场。

**Architecture:** 三类产物。**脚本层**是 9 个 CLI 工具，负责生成与机器校验六份事实源文件；**文档层**是 SOP、验收规范、选题评估卡与 30 张 prompt 卡，是人读人用的判据；**压测层**用 2025 高教社杯 A–E（含真实附件）跑端到端，用 2025 研究生六题（仅题面）校准拥挤度判据。脚本与文档互相咬合：`check_structure.py`/`check_numbers.py` 是 V1/V3 判据的机器实现，卡片产出的文件必须由脚本判绿才算过。

**Tech Stack:** Python 3.10（conda env `ptg`）、pytest、openpyxl、numpy/scipy、opencv、torch+cuda（仅冒烟）、Markdown、Word/WPS 路线（无 LaTeX）。

**Spec:** `docs/superpowers/specs/2026-09-22-mcm-playbook-design.md` — 执行者与评审者都要读它，本计划里的每条判据以 spec 的编号为准。

## Global Constraints

（逐字取自 spec，每个任务隐式包含本节）

- 路径全部用正斜杠相对路径，根目录 = `数模作战包/`；工作区根为 `C:/Users/Administrator/Desktop/2025年中国研究生数学建模竞赛赛题`。
- Python 解释器**必须**用 `F:/anaconda/envs/ptg/python.exe`（bash 里写 `/f/anaconda/envs/ptg/python.exe`）。PATH 上的 `python` 是 WindowsApps 空壳，执行即失败。
- **零联网**：本计划不得从 GitHub、PyPI、网盘或任何外网下载数据。装包只允许 `https://pypi.tuna.tsinghua.edu.cn/simple`，且仅限 Task 1 列出的包。
- 本机无 LaTeX / MATLAB / R / LibreOffice / Word。论文走 Word/WPS；`.doc` 二进制文件不得尝试程序解析。
- 脚本退出码统一：`0` 通过、`1` 判据不通过、`2` 脚本自身异常。
- 事实源行格式：一行一条目，`ID|字段1|字段2|…`，`#` 开头为表头注释行，禁止用散文段落承载关键信息。
- ID 前缀固定：`SPEC.md`→`C`、`assumptions.md`→`A`、`numbers.md`→`N`、`decisions.md`→`D`、`issues.md`→`I`，编号两位起（`C01`）。
- 一切中文输出。
- **仓库禁止出现 2026 年真实赛题原文与附件**（spec §11）。今晚只提交 2025 夹具的派生产物。
- 每次 commit 只add 本任务列出的文件，禁止 `git add -A`。
- 时间盒：T1 45min、T2 75min、T3 90min、T4 20min，合计 3.8h，23:50 前收工。**超时即按 spec §10 降级顺序砍任务，不得顺延到睡觉时间。**

## File Structure

```
数模作战包/
├── SETUP.md                     Task 1 建，Task 15 补环境实测，Task 19 定稿
├── SOP-执行规范.md               Task 10
├── 验收规范.md                   Task 10
├── 选题评估卡.md                 Task 10
├── 明早上手卡.md                 Task 20（一页，从前三份文档压缩）
├── prompts/
│   ├── 0-选题.md                Task 6  （卡 0-1 … 0-5）
│   ├── 1-题面解析.md            Task 7  （卡 1-1 … 1-5）
│   ├── 2-建模.md                Task 8  （卡 2-1 … 2-3）
│   ├── 3-求解与自证.md          Task 8  （卡 3-1 … 3-5）
│   ├── 4-论文.md                Task 9  （卡 4-1 … 4-6）
│   └── 5-交接与支援.md          Task 9  （卡 5-1 … 5-6）
├── scaffold/
│   ├── project/                 Task 2 的产物模板（六份事实源空壳 + q*/ + tools/ + paper/）
│   └── scripts/
│       ├── schema.py            Task 2  行格式契约（被其余脚本 import）
│       ├── bootstrap.py         Task 2
│       ├── check_structure.py   Task 3  V1
│       ├── check_numbers.py     Task 4  V3-1
│       ├── env_lock.py          Task 5  V2-6
│       ├── coldstart.py         Task 5  V0-1
│       ├── plot_style.py        Task 5
│       ├── numbers_add.py       Task 5
│       ├── issue_add.py         Task 5
│       └── run_all.py           Task 5  V0-3
├── tests/
│   ├── test_schema.py           Task 2
│   ├── test_bootstrap.py        Task 2
│   ├── test_check_structure.py  Task 3
│   ├── test_check_numbers.py    Task 4
│   ├── test_tools.py            Task 5
│   └── fixtures/                各任务自建
└── dryrun/                      今晚压测产物，标 throwaway，明天可整目录删
    ├── fixtures/                由 bootstrap.py 在各夹具工作区生成
    ├── 3-1-拥挤度.md  3-2-D题约束.md  3-3-B题体检.md  3-5-冒烟.py  3-6-厚度.py  3-6-verify.py
    ├── count_cards.py           Task 11 卡片完整性计数器
    └── dryrun-log.md            Task 18 汇总，含修订清单
```

设计要点：`schema.py` 是唯一协议定义处——卡片要求的字段、脚本校验的字段、模板生成的字段三处必须一致，所以三者都从它派生。改协议只改一个文件。

---

## T1 地基（45min）

### Task 1: 环境基线与目录骨架

**Files:**
- Create: `数模作战包/SETUP.md`
- Create: `数模作战包/tests/conftest.py`
- Modify: `.gitignore`（追加 `dryrun/fixtures/`）

- [ ] **Step 1: 确认 pytest 可用，缺了就装（只允许 tuna 镜像）**

```bash
PY=/f/anaconda/envs/ptg/python.exe
$PY -m pytest --version || $PY -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pytest
```
Expected: 打印 pytest 版本号。若安装失败，**立即停止本计划**并告知用户——后续任务全依赖 pytest。

- [ ] **Step 2: 补齐 spec §9.3 的包，并逐个 import 验证**

```bash
PY=/f/anaconda/envs/ptg/python.exe
$PY -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple python-docx
$PY - <<'EOF'
mods = ["numpy","pandas","scipy","matplotlib","openpyxl","docx","cv2","torch","pytest"]
bad = []
for m in mods:
    try: __import__(m)
    except Exception as e: bad.append(f"{m}: {e}")
print("FAIL " + "; ".join(bad) if bad else "OK 全部可导入")
EOF
```
Expected: `OK 全部可导入`。
说明：今晚**只装 `python-docx`**（Task 10 解析格式模板要用，且是纯 Python 无编译风险）。spec §9.3 里 `numba/pulp/deap/ezdxf/xarray/netCDF4/geopandas` 等一律**明早按需再装**——今晚装一堆用不上的包，是在拿 3.8h 里最贵的时间赌明天用得到。

- [ ] **Step 3: 写 `SETUP.md`**

内容必须包含（逐条，不得概括）：
1. 解释器全路径 `F:\anaconda\envs\ptg\python.exe`，以及"PATH 上的 `python` 是 WindowsApps 空壳，执行即报未找到"这一坑；
2. Step 2 的实测输出（哪些包可用、版本号）；
3. 无 LaTeX/MATLAB/R/LibreOffice/Word → 论文 Word 路线，`.doc` 不能程序解析；
4. 装包只走 tuna 镜像；GitHub 实测不可靠（2026-09-22 晚 `git push` 三次超时）；
5. GPU：RTX 5060 Ti 16GB，torch 2.9.0+cu128；CUDA 实测结论由 Task 15 填入；
6. **环境一旦跑通即冻结**，明早不得再动 DL 环境。

- [ ] **Step 4: 建 `tests/conftest.py`，把脚本目录加入 import 路径**

```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scaffold" / "scripts"))
```

- [ ] **Step 5: 追加 .gitignore 并提交**

```bash
cd "C:/Users/Administrator/Desktop/2025年中国研究生数学建模竞赛赛题"
printf '\n# 今晚压测的临时工作区，不入库\ndryrun/fixtures/\n数模作战包/dryrun/fixtures/\n' >> .gitignore
git add .gitignore 数模作战包/SETUP.md 数模作战包/tests/conftest.py
git commit -m "chore: 作战包环境基线与 pytest 路径"
```

---

### Task 2: `schema.py` + `bootstrap.py`（六份事实源的行格式契约与生成器）

**Files:**
- Create: `数模作战包/scaffold/scripts/schema.py`
- Create: `数模作战包/scaffold/scripts/bootstrap.py`
- Test: `数模作战包/tests/test_schema.py`, `数模作战包/tests/test_bootstrap.py`

**Interfaces:**
- Consumes: 无
- Produces: `SCHEMAS: dict[str, dict]`、`FACT_FILES: tuple[str, ...]`、`ID_RE`、`parse(path) -> list[tuple[str, list[str]]]`、`build(root: Path, nq: int) -> list[Path]`。Task 3/4/5/7/9 全部依赖这些名字。

- [ ] **Step 1: 写失败测试 `tests/test_schema.py`**

```python
from pathlib import Path
import pytest
from schema import SCHEMAS, FACT_FILES, parse

def test_五份带schema_加handoff_共六份():
    assert len(SCHEMAS) == 5
    assert set(FACT_FILES) == {"SPEC.md", "assumptions.md", "numbers.md",
                               "decisions.md", "issues.md", "handoff.md"}

def test_每份前缀唯一():
    prefixes = [c["prefix"] for c in SCHEMAS.values()]
    assert len(set(prefixes)) == 5

def test_合法行能解析(tmp_path: Path):
    p = tmp_path / "SPEC.md"
    p.write_text("# id|原文引用|解读|软硬|单位|验收断言|所属小问\n"
                 'C01|"孔径30mm"|钻孔直径|H|mm|断言直径==30|q1\n', encoding="utf-8")
    assert parse(p) == [("C01", ["\x22孔径30mm\x22", "钻孔直径", "H", "mm", "断言直径==30", "q1"])]

def test_字段数不足报错(tmp_path: Path):
    p = tmp_path / "SPEC.md"
    p.write_text("C01|只有两个\n", encoding="utf-8")
    with pytest.raises(ValueError, match="需 6 字段"):
        parse(p)

def test_前缀不匹配报错(tmp_path: Path):
    p = tmp_path / "numbers.md"
    p.write_text("X01|1|mm|a.py|b|c|d\n", encoding="utf-8")
    with pytest.raises(ValueError, match="前缀应为 N"):
        parse(p)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd 数模作战包 && /f/anaconda/envs/ptg/python.exe -m pytest tests/test_schema.py -q`
Expected: `ModuleNotFoundError: No module named 'schema'`（collection error）。

- [ ] **Step 3: 写 `schema.py`**

```python
"""六份事实源的行格式契约。改协议只改这一个文件。"""
from __future__ import annotations
import re
from pathlib import Path

SCHEMAS = {
    "SPEC.md":        dict(prefix="C", fields=["原文引用", "解读", "软硬", "单位", "验收断言", "所属小问"]),
    "assumptions.md": dict(prefix="A", fields=["内容", "理由", "影响面", "验证方式", "若为假后果"]),
    "numbers.md":     dict(prefix="N", fields=["值", "单位", "来源脚本", "出现位置", "复算方式"]),
    "decisions.md":   dict(prefix="D", fields=["决策", "备选", "理由", "放弃代价", "时间"]),
    "issues.md":      dict(prefix="I", fields=["定位", "类别", "影响面", "当前假设", "建议验证",
                                               "优先级", "复现命令", "owner", "状态"]),
}
FACT_FILES = ("SPEC.md", "assumptions.md", "numbers.md", "decisions.md", "issues.md", "handoff.md")
HANDOFF_SECTIONS = ["当前状态", "已排除路线及原因", "最可疑三处", "下一步三条"]
ID_RE = re.compile(r"^([A-Z])(\d{2,})\|(.*)$")


def parse(path: Path) -> list[tuple[str, list[str]]]:
    """跳过 # 注释与空行，返回 [(ID, [字段...])]。格式不符抛 ValueError。"""
    out = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = ID_RE.match(line)
        if not m:
            raise ValueError(f"{path.name}:{lineno} 不是合法条目行: {raw[:40]}")
        prefix, num, rest = m.groups()
        schema = SCHEMAS[path.name]
        if prefix != schema["prefix"]:
            raise ValueError(f"{path.name}:{lineno} ID 前缀应为 {schema['prefix']}，实为 {prefix}")
        fields = [f.strip() for f in rest.split("|")]
        want = len(schema["fields"])
        if len(fields) != want:
            raise ValueError(f"{path.name}:{lineno} 需 {want} 字段，实为 {len(fields)}")
        out.append((f"{prefix}{num}", fields))
    return out


def header(name: str) -> str:
    schema = SCHEMAS[name]
    return "# id|" + "|".join(schema["fields"])
```

- [ ] **Step 4: 跑测试确认通过**

Run: `/f/anaconda/envs/ptg/python.exe -m pytest tests/test_schema.py -q`
Expected: `5 passed`

- [ ] **Step 5: 写失败测试 `tests/test_bootstrap.py`**

```python
from pathlib import Path
from bootstrap import build
from schema import FACT_FILES

def test_建一个小问的完整工作区(tmp_path: Path):
    made = build(tmp_path, nq=1)
    for name in FACT_FILES:
        assert (tmp_path / name).exists(), name
    q1 = tmp_path / "q1"
    assert (q1 / "spec.md").exists()
    assert (q1 / "src").is_dir()
    assert (q1 / "results").is_dir()
    assert (q1 / "verify.py").exists()
    assert (tmp_path / "paper" / "sections").is_dir()
    assert made

def test_幂等不覆盖已有内容(tmp_path: Path):
    build(tmp_path, nq=1)
    (tmp_path / "SPEC.md").write_text('C01|"x"|y|H|mm|z|q1\n', encoding="utf-8")
    build(tmp_path, nq=2)
    assert "C01" in (tmp_path / "SPEC.md").read_text(encoding="utf-8")
    assert (tmp_path / "q2" / "verify.py").exists()
```

- [ ] **Step 6: 跑测试确认失败**

Run: `/f/anaconda/envs/ptg/python.exe -m pytest tests/test_bootstrap.py -q`
Expected: `ModuleNotFoundError: No module named 'bootstrap'`

- [ ] **Step 7: 写 `bootstrap.py`**

```python
"""生成一题的工作区。用法：python bootstrap.py <root> <小问数>"""
from __future__ import annotations
import argparse
from pathlib import Path

from schema import FACT_FILES, HANDOFF_SECTIONS, header, SCHEMAS

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
    _write(root / "data" / "REPORT.md", "# 附件数据体检报告\n\n## 文件清单\n\n## 结构与类型\n\n## 异常与缺失\n\n## 单位与坐标系\n", made)
    _write(root / "tools" / "units.py", '"""唯一允许的单位换算处。明天按题面填。"""\n\nMM_PER_PX = None\n', made)
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
```

- [ ] **Step 8: 跑测试确认通过**

Run: `/f/anaconda/envs/ptg/python.exe -m pytest tests/test_bootstrap.py -q`
Expected: `2 passed`

- [ ] **Step 9: 提交**

```bash
git add 数模作战包/scaffold/scripts/schema.py 数模作战包/scaffold/scripts/bootstrap.py 数模作战包/tests/test_schema.py 数模作战包/tests/test_bootstrap.py
git commit -m "feat: 六份事实源的行格式契约与工作区生成器"
```

---

### Task 3: `check_structure.py`（V1 结构验收）

**Files:**
- Create: `数模作战包/scaffold/scripts/check_structure.py`
- Test: `数模作战包/tests/test_check_structure.py`

**Interfaces:**
- Consumes: Task 2 的 `parse`、`FACT_FILES`、`SCHEMAS`
- Produces: `check(root: Path) -> list[str]`（问题描述列表，空列表即通过）、`main(argv) -> int`

- [ ] **Step 1: 写失败测试**

```python
from pathlib import Path
from bootstrap import build
from check_structure import check

def _ok(tmp_path):
    build(tmp_path, nq=1)
    (tmp_path / "SPEC.md").write_text(
        '# id|原文引用|解读|软硬|单位|验收断言|所属小问\nC01|"a"|b|H|mm|c|q1\n', encoding="utf-8")
    return tmp_path

def test_干净工作区通过(tmp_path):
    assert check(_ok(tmp_path)) == []

def test_抓到占位符(tmp_path):
    r = _ok(tmp_path)
    (r / "q1" / "spec.md").write_text("这里待补\n", encoding="utf-8")
    assert any("占位符" in p for p in check(r))

def test_抓到空章节(tmp_path):
    r = _ok(tmp_path)
    (r / "data" / "REPORT.md").write_text("# 标题\n\n## 空节\n\n## 有内容\n写点东西\n", encoding="utf-8")
    assert any("空章节" in p for p in check(r))

def test_抓到缺文件(tmp_path):
    r = _ok(tmp_path)
    (r / "q1" / "verify.py").unlink()
    assert any("verify.py" in p for p in check(r))

def test_抓到坏行格式(tmp_path):
    r = _ok(tmp_path)
    (r / "SPEC.md").write_text("# 头\n散文里塞了约束 C99\n", encoding="utf-8")
    assert any("SPEC.md" in p for p in check(r))

def test_抓到numbers来源脚本不存在(tmp_path):
    r = _ok(tmp_path)
    (r / "numbers.md").write_text(
        "# id|值|单位|来源脚本|出现位置|复算方式\nN01|30|mm|tools/nope.py|摘要|复算\n", encoding="utf-8")
    assert any("来源脚本" in p for p in check(r))

def test_抓到issue缺复现命令(tmp_path):
    r = _ok(tmp_path)
    (r / "issues.md").write_text(
        "# id|定位|类别|影响面|当前假设|建议验证|优先级|复现命令|owner|状态\n"
        "I01|q1|实现|无|无|无|P0||甲|open\n", encoding="utf-8")
    assert any("复现命令" in p for p in check(r))
```

- [ ] **Step 2: 跑测试确认失败**

Run: `/f/anaconda/envs/ptg/python.exe -m pytest tests/test_check_structure.py -q`
Expected: `ModuleNotFoundError: No module named 'check_structure'`

- [ ] **Step 3: 写 `check_structure.py`**

```python
"""V1 结构验收。用法：python check_structure.py <root>  退出码 0=通过 1=不通过 2=异常"""
from __future__ import annotations
import re
import sys
from pathlib import Path

from schema import FACT_FILES, SCHEMAS, parse

PLACEHOLDER = re.compile(r"TODO|TBD|FIXME|待补|占位|XXX|此处填写")

def _check_placeholders(root: Path) -> list[str]:
    out = []
    for p in sorted(root.rglob("*.md")):
        if "fixtures" in p.parts or "data/raw" in str(p).replace("\\", "/"):
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if PLACEHOLDER.search(line) and "禁止" not in line and "占位符" not in line:
                out.append(f"占位符 {p.relative_to(root)}:{i}: {line.strip()[:60]}")
    return out

def _check_empty_sections(root: Path) -> list[str]:
    out = []
    for p in sorted(root.rglob("*.md")):
        if "fixtures" in p.parts:
            continue
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
        if name == "handoff.md":
            if "（必填）" in p.read_text(encoding="utf-8"):
                out.append("handoff.md 仍有未填的（必填）小节")
            if len(p.read_text(encoding="utf-8").strip().splitlines()) < 6:
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
    for q in sorted(p for p in root.glob("q*") if re.fullmatch(r"q\d+", p.name)):
        for need in ("spec.md", "verify.py"):
            if not (q / need).exists():
                out.append(f"缺 {q.name}/{need}")
        for d in ("src", "results"):
            if not (q / d).is_dir():
                out.append(f"缺目录 {q.name}/{d}")
    if not list(root.glob("q*")):
        out.append("没有任何 q*/ 小问目录")
    return out

def check(root: Path) -> list[str]:
    return (_check_fact_files(root) + _check_questions(root)
            + _check_placeholders(root) + _check_empty_sections(root))

def main(argv=None) -> int:
    root = Path(argv[1] if len(argv or sys.argv) > 1 else ".")
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `/f/anaconda/envs/ptg/python.exe -m pytest tests/test_check_structure.py -q`
Expected: `7 passed`。若"空章节"那条用例失败，检查 `_check_empty_sections` 的 while/else 分支——这是最容易写错的一处。

- [ ] **Step 5: 提交**

```bash
git add 数模作战包/scaffold/scripts/check_structure.py 数模作战包/tests/test_check_structure.py
git commit -m "feat: V1 结构验收脚本（占位符/空章节/行格式/交付物完备性）"
```

---

### Task 4: `check_numbers.py`（V3-1 数字一致性）

**Files:**
- Create: `数模作战包/scaffold/scripts/check_numbers.py`
- Test: `数模作战包/tests/test_check_numbers.py`

**Interfaces:**
- Consumes: Task 2 的 `parse`
- Produces: `load_ledger(root) -> dict[str, str]`、`scan(sections: list[Path], ledger) -> dict`（键 `total/linked/unresolved/dup_ids`）、`main(argv) -> int`

- [ ] **Step 1: 写失败测试**

```python
from pathlib import Path
from bootstrap import build
from check_numbers import scan

def _sec(tmp_path, text):
    p = tmp_path / "paper" / "sections" / "01.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return [p]

def test_带引用的数字算已链接(tmp_path):
    s = _sec(tmp_path, "孔径为 30 mm [N01]。\n")
    assert scan(s, {"N01": "30"})["total"] == 1
    assert scan(s, {"N01": "30"})["linked"] == 1
    assert scan(s, {"N01": "30"})["unresolved"] == []

def test_无来源数字被记为未链接(tmp_path):
    s = _sec(tmp_path, "我们得到 42.7 秒。\n")
    r = scan(s, {"N01": "30"})
    assert r["total"] == 1 and r["linked"] == 0

def test_引用了台账不存在的ID(tmp_path):
    s = _sec(tmp_path, "耗时 5 s [N77]。\n")
    assert scan(s, {"N01": "30"})["unresolved"] == ["N77"]

def test_章节号与公式编号不误判(tmp_path):
    s = _sec(tmp_path, "如表 3 所示 [N01]，式 (2) 给出 30 [N01]。\n")
    r = scan(s, {"N01": "30"})
    assert r["linked"] == r["total"]
```

- [ ] **Step 2: 跑测试确认失败**

Run: `/f/anaconda/envs/ptg/python.exe -m pytest tests/test_check_numbers.py -q`
Expected: `ModuleNotFoundError: No module named 'check_numbers'`

- [ ] **Step 3: 写 `check_numbers.py`**

```python
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
    p = root / "numbers.md"
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
    argv = argv or sys.argv
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `/f/anaconda/envs/ptg/python.exe -m pytest tests/test_check_numbers.py -q`
Expected: `4 passed`

- [ ] **Step 5: 跑全量测试并提交**

```bash
cd 数模作战包 && /f/anaconda/envs/ptg/python.exe -m pytest tests/ -q
git add 数模作战包/scaffold/scripts/check_numbers.py 数模作战包/tests/test_check_numbers.py
git commit -m "feat: V3-1 数字台账引用一致性检查"
```
Expected: 全部通过（约 18 passed）。

---

### Task 5: 其余 6 个脚本（最小可用版）

**Files:**
- Create: `env_lock.py`、`coldstart.py`、`plot_style.py`、`numbers_add.py`、`issue_add.py`、`run_all.py`（均在 `scaffold/scripts/`）
- Test: `数模作战包/tests/test_tools.py`

**Interfaces:**
- Consumes: Task 2 的 `parse`、`SCHEMAS`、`header`
- Produces: 各脚本的 `main(argv) -> int`；`coldstart.pack(root) -> str`；`run_all.run(root) -> list[tuple[str, int]]`

- [ ] **Step 1: 写失败测试 `tests/test_tools.py`**

```python
import subprocess, sys
from pathlib import Path
from bootstrap import build
from coldstart import pack
from numbers_add import add as num_add
from issue_add import add as issue_add
from run_all import run as run_all

S = Path(__file__).resolve().parents[1] / "scaffold" / "scripts"

def test_numbers_add_追加一行且能被parse读回(tmp_path):
    build(tmp_path, nq=1)
    num_add(tmp_path, value="30", unit="mm", source="tools/units.py",
            where="摘要", recompute="verify.py")
    assert "N01" in (tmp_path / "numbers.md").read_text(encoding="utf-8")

def test_issue_add_缺复现命令时拒绝(tmp_path):
    build(tmp_path, nq=1)
    try:
        issue_add(tmp_path, loc="q1", kind="实现", impact="无", assume="无",
                  verify="无", pri="P0", repro="", owner="甲")
    except ValueError as e:
        assert "复现命令" in str(e)
    else:
        raise AssertionError("应当拒绝空复现命令")

def test_coldstart_打包四样输入(tmp_path):
    build(tmp_path, nq=1)
    text = pack(tmp_path, problem_text="题面正文示例")
    for need in ("题面原文", "SPEC.md", "issues.md", "目录树"):
        assert need in text

def test_run_all_无结果文件时返回非零(tmp_path):
    build(tmp_path, nq=1)
    assert any(code != 0 for _, code in run_all(tmp_path)) or run_all(tmp_path) == []
```

- [ ] **Step 2: 跑测试确认失败**

Run: `/f/anaconda/envs/ptg/python.exe -m pytest tests/test_tools.py -q`
Expected: `ModuleNotFoundError`

- [ ] **Step 3: 写 6 个脚本**

`env_lock.py` — V2-6：
```python
"""用法：python env_lock.py <root> → 写 root/env.lock"""
import platform, subprocess, sys
from pathlib import Path
def main(argv=None):
    argv = argv or sys.argv
    root = Path(argv[1] if len(argv) > 1 else ".")
    try:
        import torch
        cuda = torch.cuda.is_available()
        gputxt = torch.cuda.get_device_name(0) if cuda else "NO CUDA"
        ver = torch.__version__
    except Exception as e:
        gputxt, ver = f"torch 不可用: {e}", "?"
    lines = [f"python {sys.version.split()[0]} ({sys.executable})", platform.platform(),
             f"torch {ver}; GPU: {gputxt}",
             f"pip freeze 包数 {subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True).stdout.count(chr(10))}",
             "seed 约定：所有随机实验必须显式 seed=42 并在 spec.md 里记"]
    (root / "env.lock").write_text("\n".join(lines), encoding="utf-8")
    print(f"写 {root/'env.lock'}")
    return 0
if __name__ == "__main__":
    sys.exit(main())
```

`numbers_add.py`：
```python
"""追加一条数值台账。用法：python numbers_add.py <root> <值> <单位> <来源脚本> <出现位置> <复算方式>"""
import sys
from pathlib import Path
from schema import header, parse, SCHEMAS
def add(root: Path, **kw) -> str:
    root = Path(root); p = root / "numbers.md"
    if not p.exists():
        p.write_text(header("numbers.md") + "\n", encoding="utf-8")
    fields = [kw["value"], kw["unit"], kw["source"], kw["where"], kw["recompute"]]
    if any(not f.strip() for f in fields):
        raise ValueError("numbers 五个字段均不得为空")
    if not (root / kw["source"]).exists():
        raise ValueError(f"来源脚本不存在: {kw['source']}")
    eid = f"N{max([int(e[1:]) for e, _ in parse(p)] or [0]) + 1:02d}"
    with p.open("a", encoding="utf-8") as f:
        f.write(eid + "|" + "|".join(fields) + "\n")
    return eid
def main(argv=None):
    a = argv or sys.argv
    print("已登记 " + add(Path(a[1]), value=a[2], unit=a[3], source=a[4], where=a[5], recompute=a[6]))
    return 0
if __name__ == "__main__":
    try: sys.exit(main())
    except Exception as e: print(f"[ERROR] {e}"); sys.exit(1)
```

`issue_add.py`（与 numbers_add 同构，差异：9 字段，**`repro` 为空即 `raise ValueError("缺复现命令，拒绝登记")`**，owner 非空校验，ID 用 `I{n:02d}`，字段顺序严格照 `SCHEMAS["issues.md"]`）：
```python
"""用法：python issue_add.py <root> <定位> <类别> <影响面> <当前假设> <建议验证> <优先级> <复现命令> <owner>"""
import sys
from pathlib import Path
from schema import header, parse
FIELDS = ["定位", "类别", "影响面", "当前假设", "建议验证", "优先级", "复现命令", "owner", "状态"]
def add(root: Path, loc, kind, impact, assume, verify, pri, repro, owner) -> str:
    root = Path(root); p = root / "issues.md"
    if not p.exists():
        p.write_text(header("issues.md") + "\n", encoding="utf-8")
    if not repro.strip():
        raise ValueError("缺复现命令，拒绝登记：未登记的瑕疵是事故")
    if not owner.strip():
        raise ValueError("缺 owner：一个条目必须只有一个 owner")
    fields = [loc, kind, impact, assume, verify, pri, repro, owner, "open"]
    n = max([int(e[1:]) for e, _ in parse(p)] or [0]) + 1
    eid = f"I{n:02d}"
    with p.open("a", encoding="utf-8") as f:
        f.write(eid + "|" + "|".join(fields) + "\n")
    return eid
def main(argv=None):
    a = argv or sys.argv
    print("已登记 " + add(Path(a[1]), *a[2:10]))
    return 0
if __name__ == "__main__":
    try: sys.exit(main())
    except Exception as e: print(f"[ERROR] {e}"); sys.exit(1)
```

`coldstart.py` — V0-1：
```python
"""打包冷启动输入：题面原文 + SPEC.md + issues.md + 目录树。用法：python coldstart.py <root> [题面文件]"""
import sys
from pathlib import Path
def pack(root: Path, problem_text: str = "") -> str:
    root = Path(root)
    tree = "\n".join(sorted(str(p.relative_to(root)).replace("\\", "/")
                            for p in root.rglob("*") if p.is_file() and "fixtures" not in p.parts))
    return (f"===== 冷启动输入（只允许读这些，读完须复述：每问要算什么/现在到哪/下一步三条）=====\n\n"
            f"## 题面原文\n{problem_text or '（未提供）'}\n\n"
            f"## SPEC.md\n{(root/'SPEC.md').read_text(encoding='utf-8')}\n\n"
            f"## issues.md\n{(root/'issues.md').read_text(encoding='utf-8')}\n\n"
            f"## 目录树\n{tree}\n")
def main(argv=None):
    a = argv or sys.argv
    root = Path(a[1] if len(a) > 1 else ".")
    text = ""
    if len(a) > 2:
        text = Path(a[2]).read_text(encoding="utf-8")
    out = root / "log" / "coldstart.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(pack(root, text), encoding="utf-8")
    print(f"写 {out}（{len(pack(root, text))} 字）。把它喂给一个全新会话，"
          f"再与 handoff.md 比对，命中 <80% 即移交包欠规格")
    return 0
if __name__ == "__main__":
    sys.exit(main())
```

`plot_style.py`：
```python
"""统一 matplotlib 风格。用法：from plot_style import apply; apply()  """
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
def apply():
    plt.rcParams.update({
        "font.sans-serif": ["Microsoft YaHei", "SimHei"], "axes.unicode_minus": False,
        "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
        "lines.linewidth": 1.4, "figure.dpi": 120, "savefig.dpi": 300,
        "axes.grid": True, "grid.alpha": 0.3,
        "axes.prop_cycle": plt.cycler(color=["#222222", "#555555", "#888888",
                                             "#444444", "#777777"]),
    })
def savefig(fig, path):
    """双份输出 pdf(矢量)+png(300dpi)，供 V3-4 判据。"""
    p = str(path).rsplit(".", 1)[0]
    fig.savefig(p + ".pdf", bbox_inches="tight"); fig.savefig(p + ".png", bbox_inches="tight")
```

`run_all.py` — V0-3：
```python
"""一键复现：依次跑 q*/src/main.py 再跑 q*/verify.py。用法：python run_all.py <root>"""
import subprocess, sys
from pathlib import Path
def run(root: Path) -> list[tuple[str, int]]:
    root = Path(root); out = []
    for q in sorted(p for p in root.glob("q*") if p.is_dir()):
        for script in (q / "src" / "main.py", q / "verify.py"):
            if not script.exists():
                out.append((f"{q.name}/{script.name} 不存在", 1)); continue
            r = subprocess.run([sys.executable, str(script)], cwd=q,
                               capture_output=True, text=True, timeout=1800)
            out.append((f"{q.name}/{script.name}", r.returncode))
            if r.returncode:
                print(r.stdout[-1500:], r.stderr[-1500:])
    return out
def main(argv=None):
    a = argv or sys.argv
    res = run(Path(a[1] if len(a) > 1 else "."))
    for name, code in res:
        print(f"{'OK ' if code == 0 else 'FAIL'} {name} (exit {code})")
    bad = [n for n, c in res if c != 0]
    print(f"V0-3 一键复现: {'PASS' if not bad else f'FAIL {len(bad)} 项'}")
    return 0 if not bad else 1
if __name__ == "__main__":
    try: sys.exit(main())
    except Exception as e: print(f"[ERROR] {e}"); sys.exit(2)
```

- [ ] **Step 4: 跑测试确认通过**

Run: `/f/anaconda/envs/ptg/python.exe -m pytest tests/ -q`
Expected: 全部通过。`test_run_all_无结果文件时返回非零` 若失败，是因为刚 `build` 的工作区里 `verify.py` 会抛"尚未填写"→ 返回码 1，符合断言；若拿到 `[]` 也符合（`or` 分支）。

- [ ] **Step 5: 提交**

```bash
git add 数模作战包/scaffold/scripts/ 数模作战包/tests/test_tools.py
git commit -m "feat: 剩余 6 个验收脚本（env_lock/coldstart/plot_style/numbers_add/issue_add/run_all）"
```

**T1 结束检查（必做，30 秒）**：`pytest tests/ -q` 全绿 + `python scaffold/scripts/bootstrap.py /tmp/t1 4 && python scaffold/scripts/check_structure.py /tmp/t1` 退出码 1（因为 `SPEC.md` 无条目 → 正是 V1 该有的敏感）。不敏感就回头修 Task 3，别往下走。

---

## T2 写卡（75min）

### 卡片格式（30 张全部照此，字段顺序不得变）

````markdown
### 卡 x-y  卡片名
- **触发时机**：一句，写明在哪个阶段的哪一步、跑几次
- **输入**：列出要粘进 prompt 的东西，用 `{占位变量}` 表示
- **prompt**：
```text
（可直接复制使用的正文。所有变量以 {花括号} 标出。禁止写"适当处理"这类话。）
```
- **必落文件**：输出必须写进哪个文件的哪一节，格式是什么
- **30 秒人工判定**：人只看这一条，判定耗时 ≤30s
- **已知失效模式**：≥2 条，写 AI 实际会犯的错误
- **验证状态**：未压测
````

**质量基线（gold card，全部 30 张的判据就是它）**：

````markdown
### 卡 1-1  约束抽取
- **触发时机**：P1 定题后立刻，每问一次；后续由卡 1-3 增量补漏
- **输入**：`{题面全文}`、`{已抽清单 v(n-1)，首轮为空}`
- **prompt**：
```text
你是数学建模竞赛的题面审查员。通读以下题面，输出全部约束与要求。

输出格式：每行一条，严格六字段，竖线分隔，不加解释性文字：
C编号|"题面原文逐字引用"|你的解读|H或S|单位|建议验收断言|所属小问

规则：
1. 宁滥勿缺。凡含"须/应/不得/仅/必须/应当/要求"的句子一律成条。
2. 以下这类内容也算约束，不许因"看起来不是数学条件"而漏：提交物文件名与格式、
   结果表模板的列名与列序、图表与页数要求、单位与坐标系约定、采样密度或步长参数、
   正文与附件的呈现范围限制、前置阅读要求。
3. H=硬约束（违反即方案非法），S=软约束（违反要扣分但不非法）。判不准就标 H 并写进第 4 条。
4. 不确定如何解读的，在清单之后单列【不确定】小节：
   【不确定】C编号：读法A=… / 读法B=… / 两种读法各会让哪条结论翻盘
5. 禁止补充题面没有写的假设。那属于 assumptions.md，此处不开。
6. 建议验收断言必须可执行，写成"量 与 关系 与 阈值"，禁止"合理""适当"。

题面：
{题面全文}

已有清单（在其上增量补漏，不要重复）：
{已抽清单 v(n-1)}
```
- **必落文件**：`SPEC.md`（表头行之后逐条追加）；【不确定】段落进 `issues.md`，类别填 `理解偏差`
- **30 秒人工判定**：条数是否 ≥ 题面含"须/应/不得"的句子数；随机抽 3 条，原文引用是否逐字对得上；`建议验收断言` 列里有没有"合理/适当"
- **已知失效模式**：① 漏提交物格式类约束（最常见，直接导致 V3-5 与 V1 挂）② 把领域常识当题面约束写进来，造成后续自证无据 ③ 软硬标错——把"建议"标成 H 会白白损失可行解 ④ 断言写成"应满足孔径约束"这种不可执行的话
- **验证状态**：未压测
````

### Task 6: `prompts/0-选题.md`（卡 0-1 … 0-5）

**Files:**
- Create: `数模作战包/prompts/0-选题.md`

**Interfaces:**
- Consumes: 无
- Produces: 卡 0-2 的输出格式是 spec §8.2 的 S1–S5 打分表，Task 12 的压测直接读它

- [ ] **Step 1: 写 5 张卡，逐卡要求如下**

**卡 0-1 硬门槛过滤**：prompt 须要求 AI 对每题只回答"命中/未命中 + 引用题面原文短语"，命中条件逐字照抄 spec §8.1 三类（编译原理/体系结构背景；信息论或通信 PHY 推导；专有硬件或无法获得的数据）；输出表为 `题号|命中/未命中|依据原文|一句话理由`；**判定不得含"较难/复杂/工作量大"**——那不是硬门槛，是 §8.1 三维评估的内容。失效模式必写：把"题长"当门槛；把需要领域知识但可查资料的题误杀。

**卡 0-2 拥挤度推断**：prompt 须逐字带上 spec §8.2 的五信号表与权重（S1×1.5、S2×1.2、S3×1.2、S4×1.0、S5×0.8）、归一化 `crowd∈[1,5]`、四档映射；强制输出 `题号|S1|S2|S3|S4|S5|crowd|预估选做占比|二等奖门槛线|**每条打分的题面原文依据**`；末尾强制"只用于排序与淘汰，绝对值误差 ±10 个百分点"的自我声明，并单列**机会题清单**（`S5≥4 且可达性≥3.5`）。失效模式必写：把"我们不会做"当"没人会做"（S2 系统性偏低）；忽略提交模板的存在导致 S1 判低。

**卡 0-3 三维评估（可达性/风险）**：可达性四格（完成度可交付性/评分弹性/创新展示位/AI 杠杆率）、风险五格（数据可得性/算力时间爆雷/结果不可自证/评委主观性/同质化），各 1–5 打分并附原文依据；数据可得性=1 时整题直接标"一票否决"；输出照 §8.3 决策规则给排序。失效模式：AI 倾向给所有题中庸分 → prompt 须要求"若有两题同分，说明是哪一条判据把它们区分开"。

**卡 0-4 可行性探针**：输入 `{候选题号}``{题面}``{附件清单}`，只准回答三件事，各 ≤150 字：① 最小可跑通骨架是什么（具体到"读哪个文件的哪几列 → 出哪个数"）② 最可能卡死在哪一步 ③ 有没有客观自检锚点（题面给的示例值/闭式退化情形）。产出 1 页 memo 进 `decisions.md` 附件。**明令禁止在本卡内建模**。失效模式：越界写完整模型（浪费 30min）；把"有公式"当"有锚点"。

**卡 0-5 定题裁决**：输入两候选的 memo + 三维表；输出 `D01` 一行（决策|备选|理由|放弃代价|时间），且理由必须引用 ≥2 个具体判据编号（如 S3、V3 类）；另须写出"若明天发现选错，什么信号出现时立刻换题"（换题触发条件）。失效模式：只写"综合判断更合适"；不写换题触发条件导致 D1 才发现选错也不肯换。

- [ ] **Step 2: 自查并按需修正**

Run: `/f/anaconda/envs/ptg/python.exe 数模作战包/dryrun/count_cards.py 数模作战包/prompts/0-选题.md`（Task 11 会写该脚本；此处先用肉眼核：5 个 `### 卡` 块、每块 7 个字段标签齐全、无"适当/合理/等等"式概括）
Expected: 5 张卡、7 字段齐、验证状态全为"未压测"。

- [ ] **Step 3: 提交**

```bash
git add 数模作战包/prompts/0-选题.md
git commit -m "docs: 选题组 prompt 卡 5 张（含拥挤度五信号推断）"
```

---

### Task 7: `prompts/1-题面解析.md`（卡 1-1 … 1-5）

**Files:**
- Create: `数模作战包/prompts/1-题面解析.md`

- [ ] **Step 1: 卡 1-1 约束抽取——直接照抄本计划"质量基线"里的 gold card 全文，不得改写其 prompt 正文**（唯一改动：`验证状态` 保持 `未压测`，Task 13 压完再改）

- [ ] **Step 2: 写卡 1-2 歧义分叉**：输入 `{SPEC.md 的【不确定】清单}`；强制输出每条歧义的 `读法A|读法B|各自代价|选哪个的判据|判据需要的事实从哪拿`；并要求 AI 显式声明"此歧义是否影响交付物格式"——影响格式的必须当晚上报，不能等 V3。失效模式：给出"两种读法都合理"的和稀泥结论；未指出代价不对称。

- [ ] **Step 3: 写卡 1-3 漏读自查**：prompt 正文核心是"**只看题面原文，不许看已有清单之外的任何文件**"，要求新会话反推"上一版清单最可能漏掉的 5 条"，并**要求它按类别排查**：提交物命名/列序/页数、单位与坐标系、采样与步长参数、前置阅读要求、附件之间的隐含关联。与原 `SPEC.md` 逐条 diff，新增项标 `补漏@卡1-3`。失效模式：原会话已漏的东西它同样漏（须在卡里写明"换会话、清空上下文再跑"）；为凑数把同一约束换个说法重复登记。

- [ ] **Step 4: 写卡 1-4 小问依赖与保底**：输出 `问|喂给谁|依赖哪问的结果|分值直觉|最稳交付物|若 3h 零进展的降级版是什么`；必须指出**至少一个保底小问**（最可能拿到分且依赖最少的），并写出降级版本。失效模式：把依赖图画反（下游当上游）；没有降级方案导致 3h 后只能空转。

- [ ] **Step 5: 写卡 1-5 附件数据体检**：输出格式对齐 `data/REPORT.md` 的四节（文件清单/结构与类型/异常与缺失/单位与坐标系），prompt 内须包含可执行的检查清单：文件数与题面声称是否一致 · 各文件是否同 shape · 列名与题面表头逐字比对 · 主键是否真唯一 · 数值列范围与单位（含 `-0`、字符串型数字、日期时区）· 缺失值计数与分布是否随类别偏移 · 分类字段取值集合是否闭合 · 时间/空间是否单调（不单调即采样有重复或排序错）。**要求 AI 把发现的可疑点直接写成 `I##` 候选行**（含复现命令），而不是只叙述。失效模式：只报 shape 不报语义异常；把缺失值当"数据量正常"略过。

- [ ] **Step 6: 自查 + 提交**

肉眼核 5 张卡 7 字段齐（卡 1-1 与 gold card 逐字一致）。
```bash
git add 数模作战包/prompts/1-题面解析.md
git commit -m "docs: 题面解析组 prompt 卡 5 张"
```

---

### Task 8: `prompts/2-建模.md`（3 张）+ `prompts/3-求解与自证.md`（5 张）

**Files:**
- Create: `数模作战包/prompts/2-建模.md`、`数模作战包/prompts/3-求解与自证.md`

- [ ] **Step 1: 卡 2-1 三候选模型**：强制 3 个候选（教科书标准法/结构化改进法/数据驱动法），每个候选五字段 `假设|目标函数或判据|复杂度|可解析退化的特例|失败模式`；推荐 1 个但**必须逐条写为何不选另两个**；禁止给"综合三者优点"这种不存在的东西。失效模式：三个候选其实是同一模型的三种说法；退化特例写成"参数取常见值"而非真正可解析的情形。

- [ ] **Step 2: 卡 2-2 下界与粗估**：要求**在看到任何求解结果之前**给出 `量|粗估区间|估法（量纲/极限情形/数量级）|若结果落在区间外的解释顺序`。**硬规则写进卡里：没有本卡输出，不许写求解代码。**失效模式：区间宽到无约束力（如"1 到 1e6"）；估法其实是求解代码换了个写法（不算独立）。

- [ ] **Step 3: 卡 2-3 单位坐标系与符号表约定**：输出 `tools/units.py` 的常量定义 + 一张符号表（`符号|含义|单位|取值域|首次出现于哪问`）；prompt 须要求逐项核对题面里的**每一种单位**（含 mm/px 换算、角度制与弧度、dBm 与线性功率、浓度与百分比、经纬度与直角）；任何换算只允许经 `units.py`。失效模式：漏"px↔物理长度"类换算（今晚夹具 B 题、研究生 C 题都栽在这）；符号表漏下标变体导致 V3-3 挂。

- [ ] **Step 4: 卡 3-1 求解实现**：prompt 必含"三不"（不许放宽 `SPEC.md` 任何 H 类约束、不许硬编码答案或为凑指标改阈值、不许 `except: pass` 跳过失败分支）+ 四条交付要求（固定 `seed=42`；写 `q*/src/main.py` 且可被 `run_all.py` 调；结果写 `q*/results/result.json` 含单位与时间戳；运行时长与内存占用打一行日志）。失效模式：把不可行解当"数值误差"放行；调参调到能过就宣称收敛（须要求同时输出未调参默认配置的结果）。

- [ ] **Step 5: 卡 3-2 自证包**：把 V2 六项（独立复算/量纲取值域/退化特例/约束逐条断言/边界极端输入/可复现）逐条转成 prompt 里的交付物清单，**每条要求给出具体文件与断言代码**，不许叙述"已验证"。要求 `verify.py` 头部注明所用算法路径，并静态自查"是否 import 了 src/ 下任何模块"。失效模式：`verify.py` 只复读求解代码（须要求不同算法，例：暴力枚举/解析式/另一库）；断言只覆盖最容易的约束。

- [ ] **Step 6: 卡 3-3 缺陷登记**：**强制 AI 自报 ≥3 条可疑点**，0 条视为未认真检查并必须重跑；每条按 `issues.md` 九字段输出，复现命令必须能直接粘贴运行。prompt 内嵌一句"若你认为确无可疑点，请改为写'我拒绝回答'并说明你认为本结果无任何可攻击面——这在数学建模里几乎不可能成立"。失效模式：写三条无关痛痒的"可以进一步改进"（须要求每条指明**哪条结论会被推翻**）；漏 owner。

- [ ] **Step 7: 卡 3-4 交叉复算**：写给**另一班组**的 AI 的指令，输入只有 `SPEC.md + results/ + 该问题面`，明令**不得读求解源码**；产出自己的 `verify_b.py` 与差异报告（`GOT/EXPECT/相对误差/是否 ≤ 阈值`）。若不一致，只允许输出"两种实现各自的假设差异清单"，禁止判谁对（裁决在卡 5-4）。失效模式：读了 src 后照抄（须要求把 src 目录排除在输入之外）；差异报告只给一个布尔值不给原因。

- [ ] **Step 8: 卡 3-5 调参日志**：要求以 `log/tuning.md` 表格记录 `参数组|seed|目标值|约束是否全过|耗时|结论`，并明令**论文里只允许引用台账化过的行**；未调参基线必须保留一行。失效模式：只记最好那次（造成幸存者偏差，明天 V2-1 复算不出）；把调参过程写进正文当"敏感性分析"。

- [ ] **Step 9: 自查 + 提交**

```bash
git add 数模作战包/prompts/2-建模.md 数模作战包/prompts/3-求解与自证.md
git commit -m "docs: 建模组 3 张与求解自证组 5 张 prompt 卡"
```

---

### Task 9: `prompts/4-论文.md`（6 张）+ `prompts/5-交接与支援.md`（6 张）

**Files:**
- Create: `数模作战包/prompts/4-论文.md`、`数模作战包/prompts/5-交接与支援.md`

- [ ] **Step 1: 卡 4-1 章节树先定**：输出 `paper/sections/NN-标题.md` 全套空文件（NN 两位数）+ 图/表/公式编号预分配表；**每节须写一句"本节要回答题面哪一条 C##"**；空章节过不了 V1，所以本卡必须在 P2.1 就跑完。失效模式：编号表与后续实际不符（要求编号表落文件，卡 4-3/4-4 只能读它）；漏摘要页与附录页。

- [ ] **Step 2: 卡 4-2 摘要三段式**：严格 `问题是什么|我们怎么建的（含方法名与关键假设编号 A##）|关键数字（含单位与 N## 引用）`；字数上限按官方规范（今晚从 `format2025.docx` 抽，明早以研究生规范为准）；**禁止出现"本文分析了…并提出了…"这类无数字的空转句式**——prompt 里直接给一段反例并标为禁用。失效模式：摘要求不到具体数（说明结果没真出来，须回退卡 3-2）；把假设写在正文而不写进摘要（评委第一眼看的就是摘要里的假设）。

- [ ] **Step 3: 卡 4-3 数字回填**：输入 `numbers.md` + 各节草稿，输出把所有数值替换为 `值 [N##]` 形式的正文；prompt 须要求"遇到台账里没有的数字，**停下来提问，不许自己造**"。失效模式：手抄数值导致 V3-1 同源不同值；把区间中点当结果值。

- [ ] **Step 4: 卡 4-4 图表统一风格**：强制 `from plot_style import apply, savefig`；要求每张图有单位入轴、灰度可辨（不得只靠颜色区分系列）、表头带单位；输出 pdf+png 双份并在 `paper/sections/` 里按编号引用。失效模式：图注缺失导致正文引用悬空；用双轴图掩盖量级差异（评委最反感）。

- [ ] **Step 5: 卡 4-5 评委挑刺 12 问**：要求 AI 以"打低分的评审"立场出 12 问，每问附 `攻击面|会推翻哪条结论|现在能不能答（能/不能/需补实验）|答的话证据在哪个 N##/A##`；**未处置条数 >1 即 V3-6 不过**。失效模式：12 问全是"样本量偏小"式套话（须要求至少 3 问指向具体假设编号）；自己给自己答得过于宽松。

- [ ] **Step 6: 卡 4-6 模型评价与推广**：输出 `优点|局限（须写明是哪条 A## 造成的）|改进路径（须可执行，不写"可以进一步研究"）|推广到其他情形`。失效模式：优点写成功能介绍；局限与假设表脱钩（V3-2 会挂）。

- [ ] **Step 7: 卡 5-1 handoff 生成**：按 `handoff.md` 四节输出，**"已排除路线及原因"一节强制逐条四字段**（路线|试到什么程度|为何放弃|证据文件路径），并要求 AI 从 `log/` 与 `issues.md` 里挖，不得只凭印象；"最可疑三处"必须引 `I##`。失效模式：把排除路线写成失败流水账看不出教训；漏写"什么条件下值得重试"（后一班因此重踩坑，这是本卡存在的唯一理由）。

- [ ] **Step 8: 卡 5-2 冷启动测试**：说明先跑 `coldstart.py`，再把产物喂给**已清空上下文的新会话**，只准问三句（每问要算什么/现在到哪/下一步三条），然后与 `handoff.md` 逐项比对给命中率与缺口清单。失效模式：在原会话里跑（上下文污染，命中率虚高——本卡最易被糊弄过去）；命中率不打折自评。

- [ ] **Step 9: 卡 5-3 I## 分派 / 卡 5-4 冲突仲裁 / 卡 5-5 每日站会快照 / 卡 5-6 提交前硬闸检查**
  - **5-3**：按 `I##` 生成分派表 `I##|owner|预计耗时|依赖哪个 I##|完成后跑哪个脚本`；要求同一时刻一个 owner 手上 ≤2 条，且**禁止两个 owner 碰同一文件**。
  - **5-4**：两班 AI 结论冲突时的指令：只允许引用 `C##/A##/N##` 与断言输出作为证据，禁止"模型更合理"式论述；裁决结果写 `D##` 并回写台账。
  - **5-5**：站会快照卡，10min：跑 `check_structure.py` + `check_numbers.py` + `run_all.py`，输出"三脚本状态 + 时间盒偏差 + P0 未关存量 + 用户本时段是否产生代码提交（若有即为违规，仲裁位空缺）"，并**逐项报 spec §6 的 5 个 KPI 实测值**（瑕疵在册率、约束覆盖率、数字台账引用率、一键复现成功率、冷启动通过率）——KPI 若无人每次报数，明天不会有人真去算。
  - **5-6**：提交前 90min 硬闸检查卡，逐项跑 V3 七条 + 结果文件命名格式比对 + PDF 导出与上传演练，任一 FAIL 即**停止内容修改只做格式**，并输出提交清单。

- [ ] **Step 10: 自查 + 提交**

```bash
git add 数模作战包/prompts/4-论文.md 数模作战包/prompts/5-交接与支援.md
git commit -m "docs: 论文组与交接支援组 12 张 prompt 卡"
```

---

### Task 10: 三份规范文档 + 抽取格式判据

**Files:**
- Create: `数模作战包/SOP-执行规范.md`、`数模作战包/验收规范.md`、`数模作战包/选题评估卡.md`
- Create: `数模作战包/dryrun/format-rules.md`（判据来源，非交付物）
- Depends: 用户已把 `format2025.doc` 用 WPS 另存为 `format2025.docx`

- [ ] **Step 1: 抽取官方格式规范的判据**

```bash
/f/anaconda/envs/ptg/python.exe - <<'EOF'
from docx import Document
d = Document(r"C:/Users/Administrator/Desktop/CUMCM2025Problems/format2025.docx")
for p in d.paragraphs:
    if p.text.strip():
        print(f"[{p.style.name}] {p.text}")
for t in d.tables:
    print("--- 表格 ---")
    for row in t.rows:
        print(" | ".join(c.text.strip() for c in row.cells))
EOF
```
把输出中**每一条可判定的格式要求**（页边距、字号、字体、摘要页、编号页、页数、参考文献格式、附录要求）逐行抄进 `dryrun/format-rules.md`，标注"本专科规范，明早以研究生规范复核"。若用户尚未转换 `.docx`，**跳过本步继续 Step 2**，并在 `验收规范.md` 的 V3-5 行标注"判据待抽取"。

- [ ] **Step 2: 写 `验收规范.md`**

内容**逐字搬运** spec §5–§7：R1/R2/R3 三个审查会（含各自分工与不通过动作）、V0 五条、V1 检查项、V2 六条（含阈值）、V3 七条、5 个 KPI、角色矩阵、多 AI 防腐四条、`SPEC.md` 只读规则。
开头必须放三行导航：① `R###` 是审查会、`V#` 是判据；② 初版"完成"的定义 = 完整骨架 + 瑕疵全登记 + 可一键复现，**不含结果正确**；③ 登记过的瑕疵是资产，未登记的是事故。
末尾附脚本对照表（哪个判据由哪个脚本跑、命令原文）。

- [ ] **Step 3: 写 `SOP-执行规范.md`**

内容：§4 阶段与时间盒表 → §4.1 五条砍单线（**放最前面，明天最容易忘的是这个**）→ §8.1 P0 排期表（含"拥挤度不等附件、下载与选题并行"的并行规则）→ §8.4 P1–P2 步骤与硬规则 → §6 值守节奏 → 卡片索引表（30 张：编号|名称|何时用）→ **首页加粗一句**："明天新增的不是卡片，是卡片的输入。卡片今晚已定，只替换 `{题面全文}`。" 以及"16 张未压测卡首次使用时先在低风险小问上试一次"。

- [ ] **Step 4: 写 `选题评估卡.md`**

§8.1 硬门槛三类（逐字）+ 三维判据 + §8.2 五信号表与权重与四档映射 + 两条使用规则（只用于排序、机会题例外）+ §8.3 决策规则原文。

- [ ] **Step 5: 自查——三份文档必须无占位符**

Run: `/f/anaconda/envs/ptg/python.exe -m py_compile 数模作战包/scaffold/scripts/*.py && grep -nE "TBD|待定|待补|适当|等等" 数模作战包/*.md || echo "无占位词"`
Expected: `无占位词`（若 V3-5 因 `.docx` 未转标了"判据待抽取"，属**已登记的显式缺陷**，须在 `issues.md` 里开一条 `I##`，不许只是文档里一句话）。

- [ ] **Step 6: 提交**

```bash
git add 数模作战包/SOP-执行规范.md 数模作战包/验收规范.md 数模作战包/选题评估卡.md 数模作战包/dryrun/format-rules.md
git commit -m "docs: 执行规范、验收规范与选题评估卡三份正式文档"
```

---

### Task 11: 卡片完整性计数器

**Files:**
- Create: `数模作战包/dryrun/count_cards.py`

- [ ] **Step 1: 写脚本**

```python
"""今晚专用：数卡片、查七字段。用法：python count_cards.py <prompts目录>"""
import re, sys
from pathlib import Path
FIELDS = ["触发时机", "输入", "prompt", "必落文件", "30 秒人工判定", "已知失效模式", "验证状态"]
def main(d):
    bad, total = [], 0
    for p in sorted(Path(d).glob("*.md")):
        blocks = re.split(r"^### 卡 ", p.read_text(encoding="utf-8"), flags=re.M)[1:]
        for b in blocks:
            total += 1
            name = b.splitlines()[0].strip()
            missing = [f for f in FIELDS if f"**{f}" not in b]
            if missing:
                bad.append(f"{name}: 缺 {missing}")
            if "未压测" not in b and "已压测" not in b and "已修订" not in b:
                bad.append(f"{name}: 验证状态取值非法")
    print(f"卡片总数 {total}")
    for x in bad:
        print("[FAIL]", x)
    print("PASS" if not bad else f"FAIL {len(bad)} 项")
    return 0 if not bad else 1
if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
```

- [ ] **Step 2: 跑，Expected 输出 `卡片总数 30` 且 `PASS`**

Run: `/f/anaconda/envs/ptg/python.exe 数模作战包/dryrun/count_cards.py 数模作战包/prompts`
若少于 30，回头补：**spec 里的卡数组的是 5+5+3+5+6+6=30，少一张说明某组被偷偷省了**。

- [ ] **Step 3: 提交**

```bash
git add 数模作战包/dryrun/count_cards.py
git commit -m "chore: 卡片七字段完整性计数器（今晚专用）"
```

**T2 结束检查**：`count_cards.py` 报 30/PASS；三脚本 `pytest` 仍全绿；`grep -c "未压测" prompts/*.md` 总和 = 30（一张都没提前改状态）。

---

## T3 压卡（90min）

> 每个压测任务的共同出口：把发现的缺陷**当场写进 `dryrun/dryrun-log.md`**，格式 `卡编号 | 现象 | 我改了什么 | 是否影响 spec 其他节`。只记结论不记现象等于没压。

### Task 12: 3.1 拥挤度校准（25min，夹具=研究生六题）

**Files:**
- Create: `数模作战包/dryrun/3-1-拥挤度.md`

- [ ] **Step 1: 取题面文本**（六题 PDF 已本地转好文本，若缓存丢失则重跑）

```bash
mkdir -p /tmp/mcm && cd "C:/Users/Administrator/Desktop/2025年中国研究生数学建模竞赛赛题"
for f in A B C D E F; do pdftotext -enc UTF-8 $(ls ${f}题*.pdf) /tmp/mcm/$f.txt; done
head -c 4000 /tmp/mcm/A.txt
```

- [ ] **Step 2: 跑卡 0-1 硬门槛过滤**，输出六题命中表。Expected：**A、B 命中出局**（A 需编译器/体系结构语义与 DAG 调度；B 需 MIMO-OFDM 与 ESM 推导）。

- [ ] **Step 3: 跑卡 0-2 拥挤度**，六题各给 S1–S5 + 原文依据 + crowd。Expected 顺序：**C、E、F 判为热题；D 判为数据摩擦型偏冷；A、B 高门槛**。
校准细节（这是本任务真正要验的东西）：
  - C/F 应因 S1 高（题面未给客观评价指标，弱队也敢交卷）被判挤；
  - E 应因 S2/S3 低（源域是公开 CWRU 数据集，零摩擦）被判挤，且**同质化风险应被卡 0-3 抓到**；
  - D 应因 S3 高（雷达基数据/netCDF/多源同化）被判冷，且 S5 高 → **应进"机会题清单"**；
  - 若 D 没进机会题清单，说明 `S5≥4 且可达性≥3.5` 的判据没被执行，是卡 0-2 的实现缺陷，改卡。
- [ ] **Step 4: 跑卡 0-3 三维评估并给最终排序**，与 spec §8.3 决策规则对表：结论应为 **D 或（若数据不可得则退而选 E）** 优先，且 C/F 被开放性与同质化扣分。
- [ ] **Step 5: 权重修订与记录**：若顺序不符，只调 S1–S5 权重（改 spec §8.2 与本卡 prompt，两处必须同步改，这是本计划里唯一一处"文档与 spec 双写"的地方，务必核对）；把调了什么、为什么调写进 `dryrun-log.md`。
- [ ] **Step 6: 把卡 0-1/0-2/0-3 的 `验证状态` 改为 `已压测@2025研究生六题`**

```bash
git add 数模作战包/dryrun/3-1-拥挤度.md 数模作战包/prompts/0-选题.md docs/superpowers/specs/
git commit -m "test: 拥挤度卡在校准夹具上跑通，压测 3 张选题卡"
```

---

### Task 13: 3.2 约束抽取压测（20min，夹具=高教社杯 D 题）

**Files:**
- Create: `数模作战包/dryrun/fixtures/D题/`（由 bootstrap 生成）
- Create: `数模作战包/dryrun/3-2-D题约束.md`

- [ ] **Step 1: 建夹具工作区并确认可用**

```bash
D="C:/Users/Administrator/Desktop/CUMCM2025Problems/D题"
PY=/f/anaconda/envs/ptg/python.exe
$PY 数模作战包/scaffold/scripts/bootstrap.py 数模作战包/dryrun/fixtures/D题 4
ls "$D/附件3" | head
```
Expected: `D题/附件3/` 内 8 个成对 `result*.xlsx`（`result1-1/1-2/2-1/2-2/3-1/3-2/4-1/4-2`）。**这 8 个模板就是本任务的靶心**——提交物格式约束正是卡 1-1 第 2 条规则要抓而 AI 最常漏的东西。

- [ ] **Step 2: 跑卡 1-1**，`{题面全文}` 取 `pdftotext -enc UTF-8 "$D/D题.pdf" -` 的输出（含 D 题全部小问与巷道/水流约定）。产物写进 `fixtures/D题/SPEC.md`。

- [ ] **Step 3: 跑卡 1-3 漏读自查**（必须新开会话、清空上下文），与原 `SPEC.md` 做 diff。

- [ ] **Step 4: 按 spec 判据核对覆盖度**，逐项勾验：

| 必须抽到的约束类 | 抽到? | 漏了属哪张卡的缺陷 |
|---|---|---|
| 8 个 result 模板的存在、命名、成对含义 | | 卡 1-1 规则 2 |
| 模板内列名与列序（逐字） | | 卡 1-1 规则 2 |
| 巷道坐标/断面尺寸/单位约定 | | 卡 1-1 规则 1 |
| 水流漫延的物理与时序要求 | | 卡 1-1 规则 1 |
| 逃生方案的输出（时刻、路线、人数） | | 卡 1-1 规则 1 |
| "请先阅读论文格式规范"前置要求 | | 卡 1-1 规则 2 |
| 每条 H 约束的可执行断言写法 | | 卡 3-2 |

- [ ] **Step 5: 跑卡 1-4 小问依赖与保底**（D 题四问有明确上下游：漫延模型→逃生方案），并确认**降级方案**写得出来。
- [ ] **Step 6: 把漏项与改法写进 `dryrun-log.md`；修订卡 1-1/1-3/1-4 的 prompt 正文**（至少一处：把"漏提交模板"从抽象警告改成 prompt 里的**显式清单项**——这是今晚最可能产出的真修订）。状态改 `已压测@高教社杯D题`。
- [ ] **Step 7: 提交**

```bash
git add 数模作战包/dryrun/3-2-D题约束.md 数模作战包/prompts/1-题面解析.md
git commit -m "test: 约束抽取与漏读自查压在 D 题提交模板上，修订卡 1-1/1-3/1-4"
```

---

### Task 14: 3.3 数据体检链路（15min，夹具=高教社杯 B 题）

**Files:**
- Create: `数模作战包/dryrun/fixtures/B题/`
- Create: `数模作战包/dryrun/3-3-B题体检.md`

- [ ] **Step 1: 建工作区并把 4 个附件指过来（只读，不复制大文件——用相对软路径或直接在 prompt 里给绝对路径）**

```bash
PY=/f/anaconda/envs/ptg/python.exe
$PY 数模作战包/scaffold/scripts/bootstrap.py 数模作战包/dryrun/fixtures/B题 4
$PY - <<'EOF'
import openpyxl
base = "C:/Users/Administrator/Desktop/CUMCM2025Problems/B题/附件/"
for i in range(1, 5):
    wb = openpyxl.load_workbook(f"{base}附件{i}.xlsx", read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(max_row=3, values_only=True))
    print(f"附件{i}: sheet={wb.sheetnames} rows≈{ws.max_row} cols={ws.max_column} 表头={rows[0]} 首行={rows[1]}")
    wb.close()
EOF
```
Expected: 4 个文件同构（单 sheet、≈7470 行、2 列，表头为 `波数 (cm-1)` / `反射率 (%)`）。

- [ ] **Step 2: 跑卡 1-5 数据体检**，产物写入 `fixtures/B题/data/REPORT.md`，四节齐全。

- [ ] **Step 3: 用真数据验体检卡的判据是否真的抓得到异常**。至少要求 AI 回答这四问（这些是本夹具天然埋的坑）：
  - 四个文件 shape 是否**真的**完全一致（行数逐文件核，别信"约 7470"）；
  - 波数列是否严格单调递增？步长是否恒定（`np.diff` 的 min/max/std）？不恒定即采样网格非均匀或存在重复点；
  - 反射率首行为 `0` 是物理真空点还是缺失值编码？
  - 反射率是否全部落在 [0,100]？有无 >100 或负值（若有即归一化异常）。
- [ ] **Step 4: 跑 `check_structure.py` 验 V1 敏感**

```bash
$PY 数模作战包/scaffold/scripts/check_structure.py 数模作战包/dryrun/fixtures/B题; echo "exit=$?"
```
Expected: `exit=1`，且报出 `SPEC.md 无任何约束条目`（B 题只跑了体检没跑约束抽取——**这正是 V1 该有的行为**）。然后手写一行 `C01|...` 进 `SPEC.md`，再跑一次，确认该项消失（若还有别的报错，逐条看是真缺陷还是脚本误报，误报就修脚本——这是今晚唯一能修 checker 的机会）。
- [ ] **Step 5: 用 `numbers_add.py` 登记两条真实测得值**（如 `7470|行|bootstrap.py 读取|data/REPORT.md|openpyxl max_row` 与步长统计），确认脚本对"来源脚本不存在"会拒绝。
- [ ] **Step 6: 状态改 `已压测@高教社杯B题`（卡 1-5），修订写入 `dryrun-log.md`，提交**

```bash
git add 数模作战包/dryrun/3-3-B题体检.md 数模作战包/prompts/1-题面解析.md
git commit -m "test: 数据体检卡在 7470×2 真实光谱数据上跑通，V1 敏感性已验"
```

---

### Task 15: 3.5 GPU/CV 冒烟（10min，夹具=高教社杯 E 题）

**Files:**
- Create: `数模作战包/dryrun/3-5-冒烟.py`
- Modify: `数模作战包/SETUP.md`（填环境实测段）

- [ ] **Step 1: 写冒烟脚本**

```python
"""今晚专用：验证明天的 DL/CV 路线地基。不求解任何题。"""
import glob, sys, time
import cv2, torch

print("torch", torch.__version__, "| cuda available:", torch.cuda.is_available())
if not torch.cuda.is_available():
    print("[FAIL] CUDA 不可用——明天走 CPU 路线，须相应下调模型规模预期")
    sys.exit(1)
print("device:", torch.cuda.get_device_name(0),
      "| 显存", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 1), "GB")

vids = glob.glob(r"C:/Users/Administrator/Desktop/CUMCM2025Problems/E题/附件/附件1/*.mp4")
print("视频数:", len(vids))
cap = cv2.VideoCapture(vids[0])
ok, frame = cap.read()
fps = cap.get(cv2.CAP_PROP_FPS); n = cap.get(cv2.CAP_PROP_FRAME_COUNT)
print(f"首帧读取 ok={ok} shape={None if frame is None else frame.shape} fps={fps:.2f} 帧数={n:.0f}")
cap.release()
assert ok and frame is not None, "cv2 读不到 mp4——明天视频类题不可行，必须提前知道"

t = time.time()
x = torch.from_numpy(frame).permute(2, 0, 1).float().unsqueeze(0) / 255.0
x = x.cuda()
conv = torch.nn.Conv2d(3, 64, 3, padding=1).cuda()
for _ in range(20):
    y = torch.relu(conv(x))
torch.cuda.synchronize()
print(f"单帧 20 次 conv 耗时 {(time.time()-t)*1000:.1f} ms | "
      f"峰值显存 {torch.cuda.max_memory_allocated()/1024**2:.0f} MB")
print("SMOKE PASS")
```

- [ ] **Step 2: 跑**

Run: `/f/anaconda/envs/ptg/python.exe 数模作战包/dryrun/3-5-冒烟.py`
Expected: `SMOKE PASS`。**任一 FAIL 都是今晚最有价值的发现**——它会直接改变明天选题（视频/CV 类题能不能做）与卡 0-3 的"算力与时间爆雷"打分。
- [ ] **Step 3: 把实测结论（含 torch 版本、显存、单帧耗时、视频能否解码）写进 `SETUP.md` 环境实测段**，并在 SOP 的时间盒表旁加一行注："若本机 CPU 求解更快，不要为了用 GPU 而用 GPU"。
- [ ] **Step 4: 提交**

```bash
git add 数模作战包/dryrun/3-5-冒烟.py 数模作战包/SETUP.md
git commit -m "test: GPU/CV 路线冒烟测试通过并写入 SETUP 实测段"
```

---

### Task 16: 3.6 真实计算压 V2 验收卡（15min，夹具=高教社杯 B 题最小闭式）

**Files:**
- Create: `数模作战包/dryrun/3-6-厚度.py`（A 路）、`数模作战包/dryrun/3-6-verify.py`（B 路复算）
- Create（运行产物）: `数模作战包/dryrun/3-6-result-A.json`

> 边界：只求**最小闭式计算**，不为解出 B 题。两个文件头部都写 `# throwaway: 今晚压测用，不作任何竞赛结论`。

- [ ] **Step 1: A 路——FFT 求条纹基频**

```python
# throwaway: 今晚压测用，不作任何竞赛结论
"""A 路：干涉条纹基频 f (cycle/cm) → 光程差 → 厚度 d = 1/(2·n·f)。
   n(SiC) 取题面给定值；此处以 2.6 占位，明天必须换成题面实际值并登记 C##。"""
import json, time
from pathlib import Path
import numpy as np, openpyxl

SRC = "C:/Users/Administrator/Desktop/CUMCM2025Problems/B题/附件/附件1.xlsx"
OUT = Path(__file__).with_name("3-6-result-A.json")
N_SIC = 2.6

def load(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    arr = np.array([r[:2] for r in ws.iter_rows(min_row=2, values_only=True)], dtype=float)
    wb.close()
    wn, ref = arr[:, 0], arr[:, 1]                    # cm^-1 , %
    m = np.isfinite(wn) & np.isfinite(ref) & (wn > 0)
    wn, ref = wn[m], ref[m]
    o = np.argsort(wn)
    return wn[o], ref[o]

wn, ref = load(SRC)
dwn = wn[1] - wn[0]
sig = (ref - ref.mean()) * np.hanning(len(ref))
spec = np.abs(np.fft.rfft(sig))
res = 1.0 / (len(wn) * dwn)                           # 频率分辨单元 cycle/cm
kbin = int(np.argmax(spec[1:])) + 1                   # 跳过直流 bin
freq = kbin * res
d_nm = 1.0 / (2 * N_SIC * freq) * 1e7                 # cm → nm
print(f"N={len(wn)} 步长={dwn:.4f} cm⁻¹ 分辨单元={res:.3e} 基频bin={kbin} "
      f"freq={freq:.5f} cm⁻¹ 厚度={d_nm:.0f} nm")
OUT.write_text(json.dumps({"path": "FFT", "src": SRC, "kbin": kbin, "res": res,
                           "freq_per_cm": freq, "thickness_nm": d_nm, "n_sic": N_SIC,
                           "ts": time.strftime("%F %T")}, ensure_ascii=False, indent=2),
               encoding="utf-8")
```
Run: `/f/anaconda/envs/ptg/python.exe 数模作战包/dryrun/3-6-厚度.py`
Expected: 打印正厚度值并写出 `3-6-result-A.json`。**若 `kbin ≤ 2`，说明去均值后仍有低频泄漏**——本步的产出就是把这条记成卡 3-1 的失效模式并开 `I##`，**禁止**为了好看去悄悄换预处理方式。

- [ ] **Step 2: B 路——同一输入、不同算法（自相关求周期）**

```python
# throwaway: 今晚压测用，不作任何竞赛结论
"""B 路独立复算。V2-1 的两条硬要求：① 与 A 路**同一输入文件**（不是另一份数据）
   ② 不同算法路径，本文件不得 import/exec A 路任何符号。"""
import json
from pathlib import Path
import numpy as np, openpyxl
from scipy.signal import find_peaks

SRC = "C:/Users/Administrator/Desktop/CUMCM2025Problems/B题/附件/附件1.xlsx"   # 与 A 路同一文件
A = Path(__file__).with_name("3-6-result-A.json")

wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
ws = wb[wb.sheetnames[0]]
arr = np.array([r[:2] for r in ws.iter_rows(min_row=2, values_only=True)], dtype=float)
wb.close()
wn, ref = arr[:, 0], arr[:, 1]
m = np.isfinite(wn) & np.isfinite(ref) & (wn > 0)
wn, ref = wn[m], ref[m]
o = np.argsort(wn); wn, ref = wn[o], ref[o]
dwn = wn[1] - wn[0]
sig = ref - ref.mean()
ac = np.correlate(sig, sig, "full")[len(sig) - 1:]
pk, _ = find_peaks(ac[50:], distance=20)              # 跳过零延迟主峰邻域
period_idx = int(pk[0]) + 50
freq = 1.0 / (period_idx * dwn)                       # cycle/cm
d_nm = 1.0 / (2 * 2.6 * freq) * 1e7

a = json.loads(A.read_text(encoding="utf-8"))
bins_apart = abs(freq - a["freq_per_cm"]) / a["res"]
print(f"B 路 自相关周期点={period_idx} freq={freq:.5f} 厚度={d_nm:.0f} nm | A 路={a['thickness_nm']:.0f} nm")
print(f"两路基频相差 {bins_apart:.2f} 个 FFT 分辨单元（A 路 res={a['res']:.3e}）")
print("PASS" if bins_apart <= 1.0 else f"FAIL 差 {bins_apart:.2f} bin，属预处理问题不是容差问题")
```

- [ ] **Step 3: 判据按"频率分辨单元"，不按 1e-6 —— 这是对 spec V2-1 的真修订**

Run A 后再 Run B。Expected：`bins_apart ≤ 1.0` 且打印 `PASS`。
**今晚几乎必然发生的事**：FFT 只能取整 bin，自相关给出连续周期估计，两路**不可能**吻合到 spec V2-1 写的"相对误差 ≤1e-6"。所以本步的真正产出是修订判据本身：
1. 改卡 3-2 的 V2-1 条为：`确定性闭式算法 ≤1e-6；离散谱/迭代/启发式算法须按该算法自身的分辨率或收敛阈定义容差，并在 verify.py 头部写明该分辨率是多少`；
2. **同步改 spec §6 的 V2-1 行**，并在 spec §13 追加一条修正记录（两处不一致是明天最阴险的事故源）；
3. 若 `bins_apart > 1`，那是预处理缺陷不是容差问题，开 `I##` 并在明天换题时警惕同类。
反向检查：若两路竟吻合到 1e-6 以内，第一反应应是怀疑 B 路抄了 A 路。
- [ ] **Step 4: 合成信号锚点（V2-3 退化特例的正确形态）**

真实数据没有标准答案，所以"退化特例"在这里的正确形态是**喂一段已知答案的合成信号给同一条频率估计代码**，看它能不能取回已知值。这是独立于题面数据的正确性锚点，明天任何反演/频谱类小问都用得上：

```python
import numpy as np
k_true = 0.0123                                   # 已知条纹频率 cycle/cm⁻¹
wn = np.arange(400.0, 4000.0, 0.5)
sig = 30.0 * np.cos(2 * np.pi * k_true * wn)      # 零均值，无直流泄漏
spec = np.abs(np.fft.rfft(sig * np.hanning(len(sig))))
res = 1.0 / (len(wn) * (wn[1] - wn[0]))
kbin = int(np.argmax(spec[1:])) + 1
got = kbin * res
apart = abs(got - k_true) / res
print(f"已知 {k_true:.5f}，求得 {got:.5f}，差 {apart:.2f} 个分辨单元")
assert apart <= 1.0, "A 路的频率换算或分辨单元定义写错了——Step 1/2 的结论全部作废"
```
Expected: `差 0.28 个分辨单元` 左右（`k_true/res = 44.28` → bin 44），断言通过。
**若此处失败，Step 1/2 的双路比对结果一律作废**——因为两路可能犯了同一个换算错误而互相"印证"。这就是本步骤必须存在的原因，也是明天 V2-3 的判据形态。
- [ ] **Step 5: 跑约束逐条断言（V2-4 的最小可行版）**：为这个最小计算写 ≥4 条可执行断言（波数单调、步长恒定容差 1%、反射率∈[0,100]、厚度>0），全绿。
- [ ] **Step 6: 状态改 `已压测@高教社杯B题最小计算`（卡 3-1/3-2/3-4），修订写进 `dryrun-log.md`，提交**

```bash
git add 数模作战包/dryrun/3-6-厚度.py 数模作战包/dryrun/3-6-verify.py 数模作战包/prompts/3-求解与自证.md
git commit -m "test: 双路复算压在真实光谱数据上，据结果修订卡 3-2 复算定义"
```

---

### Task 17: 3.4 冷启动测试（5min）

**Files:**
- Create: `数模作战包/dryrun/fixtures/D题/handoff.md`（由卡 5-1 生成）
- Create: `数模作战包/dryrun/3-4-冷启动.md`

- [ ] **Step 1: 用卡 5-1 为 D 题夹具写 `handoff.md`**（四节全填，"已排除路线"一节可从 Task 13 的实际漏读情况取材——"卡 1-3 首次跑未发现的约束类型"就是最真实的排除路线记录）
- [ ] **Step 2: 打包冷启动输入**

```bash
/f/anaconda/envs/ptg/python.exe 数模作战包/scaffold/scripts/coldstart.py 数模作战包/dryrun/fixtures/D题
```
- [ ] **Step 3: 开一个全新会话**（上下文必须干净；在同一会话里跑等于自评），把 `log/coldstart.txt` 贴进去，只问三句：每问要算什么 / 现在到哪 / 下一步最该做的三条。
- [ ] **Step 4: 逐项比对命中率**，写 `3-4-冷启动.md`：`比对了哪几项 | 命中 | 缺口 | 缺口归因（SPEC 欠规格 / handoff 没写 / 卡片问法不对）`。
Expected: 命中 ≥80%。**不足 80% 时不得改 handoff.md 去"迎合"，只能补 SPEC.md 与卡 5-2 的问法**——迁就输出会让这个指标失去意义。
- [ ] **Step 5: 状态改 `已压测@D题夹具`（卡 5-1/5-2），提交**

```bash
git add 数模作战包/dryrun/3-4-冷启动.md 数模作战包/prompts/5-交接与支援.md 数模作战包/dryrun/fixtures/D题/handoff.md
git commit -m "test: 冷启动交接验收真实跑通一次，据缺口修订卡 5-1/5-2"
```

---

### Task 18: T3 汇总（并入各任务，独立提交一次）

- [ ] **Step 1: 检查 `dryrun-log.md` 完整性**——必须含：每个压测任务的"卡编号|现象|改了什么|是否影响 spec 其他节"四列；spec 与卡片双写的改动逐条列出。
- [ ] **Step 2: 确认成功判据达成情况**，逐条打分并写在文件末尾：

```bash
PY=/f/anaconda/envs/ptg/python.exe
$PY 数模作战包/dryrun/count_cards.py 数模作战包/prompts
grep -c "已压测" 数模作战包/prompts/*.md
$PY -m pytest 数模作战包/tests -q
```
Expected: 卡片 30/PASS；`已压测` 计数 **≥14**；pytest 全绿；修订 ≥3 张（若为 0，见 spec §10——说明卡写得不够具体）。
- [ ] **Step 3: 提交**

```bash
git add 数模作战包/dryrun/dryrun-log.md
git commit -m "test: T3 压测汇总与卡片修订清单"
```

---

## T4 修卡打包（20min）

### Task 19: 修订回写与终检

- [ ] **Step 1: 把 `dryrun-log.md` 里的每条修订落到对应卡片正文**，状态字段改 `已修订@2026-09-22`
- [ ] **Step 2: 若某条改动影响 spec（如 V2-1 复算定义被 Task 16 改写），同步改 spec 并在 spec §13 追加一条修正记录**——两处必须一致，不一致就是明天的事故源
- [ ] **Step 3: 跑全套终检**

```bash
cd 数模作战包
PY=/f/anaconda/envs/ptg/python.exe
$PY -m pytest tests/ -q
$PY dryrun/count_cards.py prompts
$PY scaffold/scripts/bootstrap.py /tmp/final 4 && $PY scaffold/scripts/check_structure.py /tmp/final; echo "exit=$? (预期 1)"
grep -rnE "TODO|TBD|待补|待定" *.md prompts/*.md || echo "无占位词"
```
Expected: pytest 全绿；30 卡 PASS；`exit=1`（V1 敏感）；无占位词。
- [ ] **Step 4: 提交并打 tag**

```bash
git add 数模作战包/prompts/ 数模作战包/*.md docs/superpowers/specs/ docs/superpowers/plans/
git commit -m "docs: 作战包 v1.1（经本地夹具压测）" && git tag playbook-v1.1
```

### Task 20: 明早上手卡（一页）

- [ ] **Step 1: 写 `数模作战包/明早上手卡.md`**，从三份文档压缩成**一页**，只放这六块，顺序不得变：
  1. 开赛 0–60min 动作（题面到手 → 卡 0-1/0-2 与附件下载**并行**）；
  2. 前 36h 时间盒表（P0 3h / P1 5h / P2 22h）；
  3. 五条砍单线（逐字）；
  4. V0 五条判据 + 一句"登记过的瑕疵是资产，未登记的是事故"；
  5. 环境三条坑（解释器全路径 / 无 LaTeX / GitHub 不可依赖）；
  6. 卡片索引：30 张按"何时用"一行一张排列，**未压测的 16 张前面加 `⚠`**。
- [ ] **Step 2: 提交**

```bash
git add 数模作战包/明早上手卡.md
git commit -m "docs: 明早一页上手卡"
```

---

## 降级顺序（超时即砍，不得顺延睡觉）

1. 砍 Task 13 的 Step 5（卡 1-4 依赖图）——明天现场画得出来
2. 砍 Task 17（冷启动）——但须把卡 5-1/5-2 明确标 `未压测`，别假装验过
3. 砍 Task 14 的 Step 5（numbers_add 手测）
4. **绝不砍**：Task 2/3/4（checker 不敏感则整套验收空转）、Task 6/7（选题与题面卡是明天第一步）、Task 15（GPU 冒烟若不做，明天可能选了一个跑不动的题）、Task 20（一页上手卡是唯一会被真正翻阅的东西）
5. Task 8 的组 3 与 Task 16 绑定：若 16 来不及做，**组 3 五张卡全部保持 `未压测`，且不得在明天 P2.2 之前当成可靠工具**

---

## 附：计划自审记录（2026-09-22，按 writing-plans 的三项检查）

### 1. spec 覆盖检查
逐节对表 spec §1–§13：§3.1 六份事实源→Task 2；§4/§4.1 时间盒与砍单线→Task 10 Step 3 + Task 20；§5 三个审查会→Task 10 Step 2；§6 V0→Task 5(`coldstart`/`run_all`)+Task 17，V1→Task 3，V2→Task 5(`env_lock`)+Task 8/16，V3→Task 4+Task 10；§7 防腐四条→Task 8/9 卡 3-4、5-3、5-4、5-1 + Task 10；§8.1–§8.3 选题→Task 6+10+12；§8.5 30 卡→Task 6/7/8/9+11；§9.1→Task 2；§9.2 九脚本→Task 2/3/4/5；§9.3→Task 1；§10 T1–T4→Task 12–20；§11 仓库禁放 2026 原文→Global Constraints。
**两处已接受的缺口**：spec §2.4 的 C 题标为"备用"未排任务；§12 各参数默认值靠 Task 10 Step 1 与明早核对，不单独建任务。

### 2. 占位符扫描
清除了 4 处自造占位式写法：`d = 0.0 / ... if False else ...` 与 `r = json.load(...) if False else None`（两段残留的死代码三元式）、`GOT = None # 由 Step 3 注入`（把赋值推给下一步叙述）。现全部改为实际代码。

### 3. 类型与签名一致性
`parse/header/build/check/scan/load_ledger/pack/run/add` 在各 Task 的调用处与定义处逐一核对，形参名与返回结构一致；`tests/conftest.py` 的 `parents[1]/scaffold/scripts` 路径与 File Structure 一致。发现并修正 `Global Constraints 禁止 git add -A` 与 Task 19 Step 4 实际用了 `git add -A` 的自相矛盾。

### 4. 代码逻辑跑真值时发现并修掉的 6 个 bug
| # | 位置 | 症状 | 修法 |
|---|---|---|---|
| 1 | Task 3 `_check_empty_sections` | `while…else` 在"空章节后紧跟下一个标题"时把 `j` 误置为 `len(lines)`，导致**最典型的那种空章节完全查不出来**（对应单测会红） | 改为先收集所有 `## ` 下标、再按区间切，语义直白 |
| 2 | Task 4 `scan` | 结构性序号（表3、式(2)）被计入分母却不计入已链接，使"章节号不误判"那条单测必红；而正确的语义是**从分母里排除** | 新增 `STRUCTURAL` 前缀窗口判定，序号 token 不进 total |
| 3 | Task 5 `env_lock` | `"\n".join(lines)` 里混进一个 int（pip freeze 行数）→ 运行时 `TypeError` | 包数用 f-string 转成一行字符串 |
| 4 | Task 5 `numbers_add` | 先算 `n = len(parse(p))+1`，又用 `try/except pass` 覆盖一遍 → ID 在删过条目时会重复，且掩盖真实异常 | 统一为 `max(现有编号)+1`，去掉裸 except |
| 5 | Task 5 `coldstart` | `out.parent.mkdir(exist_ok=True)` 在 `log/` 不存在时抛错（用 `main()` 路径时才碰到，build 走的是另一条） | 加 `parents=True` |
| 6 | Task 16 A/B 两路 | ① B 路读的是**附件2**而非附件1，跨样本比对根本不构成复算 ② 频率换算式写成 `… if False else 1e4/(…)`，量纲错 ③ 合成信号锚点里的 `kk` 表达式与分辨单元定义不一致，断言必挂 | 两路统一附件1；厚度式改为 `1/(2·n·f)·1e7`；锚点改为按"分辨单元数"判据（`k_true/res≈44.28`→bin 44，差 0.28 单元） |

### 5. 由 bug 6 派生出的一条真修订
FFT 与自相关两条路径**不可能**吻合到 spec V2-1 写的"相对误差 ≤1e-6"——离散谱估计的天然粒度就是一个分辨单元。故 V2-1 的容差定义必须改为"**确定性闭式 ≤1e-6；离散谱/迭代/启发式按该算法自身分辨率定义容差，并在 `verify.py` 头部写明分辨率数值**"。Task 16 Step 3 要求同时改卡 3-2 与 spec §6 V2-1，并在 spec §13 记一条。**这是今晚唯一一处"计划反过来改 spec"的改动，属预期产出而非偏差**——spec 里那条 1e-6 是我坐在键盘前拍的，没经过真实计算。
