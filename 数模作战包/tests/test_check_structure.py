from pathlib import Path
from bootstrap import build
from check_structure import check
from schema import header


def _fill(root: Path) -> Path:
    """把模板自带的空壳全部填成合法内容——空白工作区本来就不该过 V1。"""
    (root / "SPEC.md").write_text(
        header("SPEC.md") + '\nC01|"孔径30mm"|钻孔直径|H|mm|assert d==30|q1\n', encoding="utf-8")
    (root / "data" / "REPORT.md").write_text(
        "# 附件数据体检报告\n\n## 文件清单\n附件1.xlsx 一个\n\n## 结构与类型\n7470 行 2 列\n\n"
        "## 异常与缺失\n反射率首行为 0\n\n## 单位与坐标系\n波数 cm⁻¹；反射率 %\n", encoding="utf-8")
    (root / "handoff.md").write_text(
        "# 交接备忘\n\n## 当前状态\nq1 已出结果\n\n## 已排除路线及原因\n无\n\n"
        "## 最可疑三处\n见 I01\n\n## 下一步三条\n补灵敏度分析\n", encoding="utf-8")
    return root


def _ok(tmp_path):
    build(tmp_path, nq=1)
    return _fill(tmp_path)


def test_空白工作区必须判红(tmp_path):
    """模板自带的空章节与未填 handoff 必须被抓到，否则 V1 形同虚设。"""
    build(tmp_path, nq=1)
    problems = check(tmp_path)
    assert any("空章节" in p for p in problems), problems
    assert any("handoff" in p for p in problems), problems
    assert any("SPEC.md 无任何约束条目" in p for p in problems), problems


def test_填齐后通过(tmp_path):
    assert check(_ok(tmp_path)) == []


def test_抓到占位符(tmp_path):
    r = _ok(tmp_path)
    (r / "q1" / "spec.md").write_text("这里待补\n", encoding="utf-8")
    assert any("占位符" in p for p in check(r))


def test_抓到空章节(tmp_path):
    r = _ok(tmp_path)
    (r / "data" / "REPORT.md").write_text(
        "# 标题\n\n## 空节\n\n## 有内容\n写点东西\n", encoding="utf-8")
    assert any("空章节" in p and "空节" in p for p in check(r))


def test_抓到末节为空(tmp_path):
    r = _ok(tmp_path)
    (r / "data" / "REPORT.md").write_text(
        "# 标题\n\n## 有内容\n写点\n\n## 尾巴空着\n", encoding="utf-8")
    assert any("空章节" in p and "尾巴" in p for p in check(r))


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
        header("numbers.md") + "\nN01|30|mm|tools/nope.py|摘要|复算\n", encoding="utf-8")
    assert any("来源脚本" in p for p in check(r))


def test_抓到issue缺复现命令(tmp_path):
    r = _ok(tmp_path)
    (r / "issues.md").write_text(
        header("issues.md") + "\nI01|q1|实现|无|无|无|P0||甲|open\n", encoding="utf-8")
    assert any("复现命令" in p for p in check(r))


def test_抓到issue缺owner(tmp_path):
    r = _ok(tmp_path)
    (r / "issues.md").write_text(
        header("issues.md") + "\nI01|q1|实现|无|无|无|P0|python x.py||open\n", encoding="utf-8")
    assert any("owner" in p for p in check(r))
