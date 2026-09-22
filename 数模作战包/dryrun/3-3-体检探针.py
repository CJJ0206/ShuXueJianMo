"""Task 14：卡 1-5 附件数据体检的可执行检查清单，拿 2025 高教社杯 B 题真光谱数据压一遍。
本脚本本身就是"体检卡"要求的检查项的代码化——明天换个题只改 FILES 与列名假设。"""
import glob
import sys

import numpy as np
import openpyxl

FILES = sorted(glob.glob("C:/Users/Administrator/Desktop/CUMCM2025Problems/B题/附件/附件*.xlsx"))
print(f"### 发现文件 {len(FILES)} 个（题面声称 4 个附件）")

data = {}
for p in FILES:
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    head, body = rows[0], rows[1:]
    arr = np.array([r[:2] for r in body], dtype=float)
    data[p.split("/")[-1]] = (head, arr)
    print(f"{p.split('/')[-1]:<12} sheets={wb.sheetnames} 表头={head[:2]} "
          f"行={len(body)} 列={arr.shape[1]}")

print("\n### 1) 各文件是否同 shape")
shapes = {k: v[1].shape for k, v in data.items()}
print(shapes, "→", "一致" if len(set(map(tuple, shapes.values()))) == 1 else "**不一致，须查明**")

print("\n### 2) 表头是否逐字相同")
heads = {k: str(v[0][:2]) for k, v in data.items()}
print(heads, "→", "一致" if len(set(heads.values())) == 1 else "**不一致**")

for k, (_, arr) in data.items():
    wn, ref = arr[:, 0], arr[:, 1]
    ok = np.isfinite(wn) & np.isfinite(ref)
    d = np.diff(wn[ok])
    print(f"\n### {k}")
    print(f"  缺失/非数值行: {int((~ok).sum())}")
    print(f"  波数单调递增: {bool(np.all(d > 0))}  | diff min={d.min():.6f} max={d.max():.6f} "
          f"std={d.std():.3e}")
    print(f"  波数步长恒定? {'是' if d.std() < 1e-9 else '**否：采样网格非均匀，傅里叶类方法须先重采样**'}")
    print(f"  波数范围: {wn[ok].min():.4f} ~ {wn[ok].max():.4f} cm⁻¹，点数 {int(ok.sum())}")
    print(f"  反射率范围: {ref[ok].min():.4f} ~ {ref[ok].max():.4f} %")
    bad = ref[ok][(ref[ok] < 0) | (ref[ok] > 100)]
    print(f"  反射率越界([0,100]外)点数: {len(bad)}" + (f" 样例 {bad[:3]}" if len(bad) else ""))
    zeros = int((ref[ok] == 0).sum())
    print(f"  反射率恰为 0 的行数: {zeros}（位置 {np.flatnonzero(ref == 0)[:5].tolist()}）"
          f" → 是真空点还是缺失值编码？两种解读会导致不同的归一化")
    dup = int(len(wn[ok]) - len(np.unique(wn[ok])))
    print(f"  波数重复值个数: {dup}")

print("\n### 结论：以上每一行『否/不一致/越界/需查明』都必须变成 issues.md 的一条 I##")
