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
