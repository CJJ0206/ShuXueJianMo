import pytest
from bootstrap import build
from coldstart import pack
from issue_add import add as issue_add
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
        issue_add(tmp_path, loc="q1", kind="实现", impact="无", assume="无",
                  verify="无", pri="P0", repro="", owner="甲")


def test_issue_add_缺owner时拒绝(tmp_path):
    build(tmp_path, nq=1)
    with pytest.raises(ValueError, match="owner"):
        issue_add(tmp_path, loc="q1", kind="实现", impact="无", assume="无",
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
