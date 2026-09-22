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
    p.write_text('# id|原文引用|解读|软硬|单位|验收断言|所属小问\n'
                 'C01|"孔径30mm"|钻孔直径|H|mm|断言直径==30|q1\n', encoding="utf-8")
    assert parse(p) == [("C01", ['"孔径30mm"', "钻孔直径", "H", "mm", "断言直径==30", "q1"])]


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


def test_字段内转义竖线不破坏切分(tmp_path: Path):
    """明天一定会用到：Excel 表头名本身含竖线（如 "端点编号\\|端点坐标"）。"""
    p = tmp_path / "SPEC.md"
    p.write_text('C01|"端点编号\\|端点坐标\\|\\|x (m)"|双行表头|H|-|assert 列名解析|全部\n',
                 encoding="utf-8")
    eid, fields = parse(p)[0]
    assert eid == "C01" and len(fields) == 6
    assert fields[0] == '"端点编号|端点坐标||x (m)"', "转义应还原为字面竖线"


def test_未转义竖线报错时给出可操作提示(tmp_path: Path):
    p = tmp_path / "SPEC.md"
    p.write_text('C01|"a|b"|c|H|-|d|q1\n', encoding="utf-8")
    with pytest.raises(ValueError, match="转义"):
        parse(p)
