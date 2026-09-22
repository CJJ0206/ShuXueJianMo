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
