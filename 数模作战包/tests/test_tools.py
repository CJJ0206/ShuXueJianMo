import pytest
import issue_add
import numbers_add
from bootstrap import build
from coldstart import pack
from issue_add import add as issue_add_fn
from numbers_add import add as num_add
from run_all import run as run_all
from schema import parse


def test_numbers_add_追加一行且能被parse读回(tmp_path):
    build(tmp_path, nq=1)
    eid = num_add(tmp_path, value="30", unit="mm", source="tools/units.py",
                  where="摘要", recompute="verify.py")
    assert eid == "N01"
    rows = parse(tmp_path / "numbers.md")
    assert rows == [("N01", ["30", "mm", "tools/units.py", "摘要", "verify.py"])]


def test_numbers_add_来源脚本不存在时拒绝(tmp_path):
    build(tmp_path, nq=1)
    with pytest.raises(ValueError, match="来源脚本不存在"):
        num_add(tmp_path, value="1", unit="x", source="nope.py", where="a", recompute="b")


def test_numbers_add_ID递增不重复(tmp_path):
    build(tmp_path, nq=1)
    assert num_add(tmp_path, value="1", unit="x", source="tools/units.py",
                   where="a", recompute="b") == "N01"
    assert num_add(tmp_path, value="2", unit="x", source="tools/units.py",
                   where="a", recompute="b") == "N02"


def test_issue_add_缺复现命令时拒绝(tmp_path):
    build(tmp_path, nq=1)
    with pytest.raises(ValueError, match="复现命令"):
        issue_add_fn(tmp_path, loc="q1", kind="实现", impact="无", assume="无",
                  verify="无", pri="P0", repro="", owner="甲")


def test_issue_add_缺owner时拒绝(tmp_path):
    build(tmp_path, nq=1)
    with pytest.raises(ValueError, match="owner"):
        issue_add_fn(tmp_path, loc="q1", kind="实现", impact="无", assume="无",
                  verify="无", pri="P0", repro="python x.py", owner="")


def test_coldstart_打包四样输入(tmp_path):
    build(tmp_path, nq=1)
    text = pack(tmp_path, problem_text="题面正文示例")
    for need in ("题面原文", "SPEC.md", "issues.md", "目录树"):
        assert need in text
    assert "题面正文示例" in text


def test_run_all_空壳verify返回非零(tmp_path):
    build(tmp_path, nq=1)
    res = run_all(tmp_path)
    assert res, "至少应报出 src/main.py 不存在"
    assert any(code != 0 for _, code in res)


def test_run_all_子进程打中文不崩(tmp_path):
    """中文 Windows 上 text=True 默认按 GBK 解码，会让 stdout 变成 None。"""
    build(tmp_path, nq=1)
    (tmp_path / "q1" / "src").mkdir(exist_ok=True)
    (tmp_path / "q1" / "src" / "main.py").write_text(
        "import sys\nsys.stderr.reconfigure(encoding='utf-8')\n"
        "print('中文进度：已处理 30% —— 触发解码陷阱')\n"
        "raise SystemExit(3)\n", encoding="utf-8")
    res = run_all(tmp_path)
    hit = [c for name, c in res if name.endswith("main.py")]
    assert hit == [3], f"子进程退出码未如实传回：{res}"


# --- CLI 包装层：上面那个 off-by-one 只有测 main() 才能抓到 ---

def test_numbers_add_CLI_正例返回0(tmp_path):
    build(tmp_path, nq=1)
    rc = numbers_add.main(["p", str(tmp_path), "30", "mm", "tools/units.py", "摘要", "verify"])
    assert rc == 0, "CLI 参数个数判错会把正例当用法错误拒掉"
    assert "N01" in (tmp_path / "numbers.md").read_text(encoding="utf-8")


def test_issue_add_CLI_正例返回0(tmp_path):
    build(tmp_path, nq=1)
    rc = issue_add.main(["p", str(tmp_path), "q1", "实现", "影响", "假设", "验证",
                         "P0", "python x.py", "甲"])
    assert rc == 0
    assert "I01" in (tmp_path / "issues.md").read_text(encoding="utf-8")


def test_CLI_缺复现命令时退出1而非2(tmp_path):
    """退出码语义：1=违反判据被拒，2=用法错误。二者不可混。"""
    build(tmp_path, nq=1)
    rc = issue_add.main(["p", str(tmp_path), "q1", "实现", "影响", "假设", "验证",
                         "P0", "", "甲"])
    assert rc == 1


def test_CLI_参数不足时退出2(tmp_path):
    build(tmp_path, nq=1)
    assert numbers_add.main(["p", str(tmp_path), "1", "mm"]) == 2
    assert issue_add.main(["p", str(tmp_path), "q1"]) == 2
