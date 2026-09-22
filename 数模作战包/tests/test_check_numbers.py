from pathlib import Path
from check_numbers import scan


def _sec(tmp_path, text):
    p = tmp_path / "paper" / "sections" / "01.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return [p]


def test_带引用的数字算已链接(tmp_path):
    s = _sec(tmp_path, "孔径为 30 mm [N01]。\n")
    r = scan(s, {"N01": "30"})
    assert r["total"] == 1 and r["linked"] == 1
    assert r["unresolved"] == []


def test_无来源数字被记为未链接(tmp_path):
    s = _sec(tmp_path, "我们得到 42.7 秒。\n")
    r = scan(s, {"N01": "30"})
    assert r["total"] == 1 and r["linked"] == 0


def test_引用了台账不存在的ID(tmp_path):
    s = _sec(tmp_path, "耗时 5 s [N77]。\n")
    assert scan(s, {"N01": "30"})["unresolved"] == ["N77"]


def test_章节号与公式编号不进分母(tmp_path):
    s = _sec(tmp_path, "如表 3 所示 [N01]，式 (2) 给出 30 [N01]。\n")
    r = scan(s, {"N01": "30"})
    assert r["total"] == 1, "只有 30 该进分母，表3 与 式(2) 是结构性序号"
    assert r["linked"] == 1


def test_ID重复引用被记为需核对(tmp_path):
    _sec(tmp_path, "孔径 30 mm [N01]。\n")
    (tmp_path / "paper" / "sections" / "02.md").write_text("另一处 30 mm [N01]。\n", encoding="utf-8")
    r = scan(sorted((tmp_path / "paper" / "sections").glob("*.md")), {"N01": "30"})
    assert r["dup_ids"] == ["N01"]
