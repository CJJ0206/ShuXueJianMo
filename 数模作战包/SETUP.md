# SETUP —— 本机环境与开工前置

实测时间 2026-09-22 晚。本文件是明天开工前唯一需要核对的环境清单。

## 1. 解释器：必须走全路径

```
F:\anaconda\envs\ptg\python.exe        ← 用这个
bash 里：/f/anaconda/envs/ptg/python.exe
```

**头号坑**：PATH 上的 `python` / `python3` 是 `WindowsApps` 空壳，执行只会打印
"Python was not found; run without arguments to install from the Microsoft Store"。
任何脚本、任何子代理，一律用全路径或先 `conda activate ptg`。

已装可用（实测导入通过）：

| 包 | 版本 | 用途 |
|---|---|---|
| numpy | 2.0.2 | 通用 |
| pandas | 2.3.2 | 表格 |
| scipy | 1.13.1 | 信号/优化/插值 |
| matplotlib | 3.10.3 | 出图（配 `plot_style.py`） |
| sklearn | 1.7.1 | 回归/分类/降维 |
| torch | 2.9.0+cu128 | DL，CUDA 12.8 |
| opencv (cv2) | 4.13.0 | 图像/视频 |
| seaborn | 0.13.2 | 统计图 |
| networkx | 3.4.2 | 图算法 |
| xgboost | 3.1.3 | 表格模型 |
| openpyxl | 3.1.5 | 读写 xlsx |
| sympy | 1.13.1 | 符号推导 |
| pytest | 9.1.1 | 本仓库脚本的测试 |
| python-docx | 1.2.0 | 读论文格式模板、导出 Word |

已知无害告警：`pip` 会打印 `Ignoring invalid distribution -umpy`（site-packages 里
一个 numpy 残留目录）。导入 numpy 正常，不必处理，别去 `pip uninstall numpy`。

未装、明早按需再装：`numba`（大图/密集循环提速）、`pywt`（小波）、`statsmodels`、
`shap`（可解释性）、`lightgbm`、`pulp` 或 `ortools`（线性/整数规划）、`deap`（遗传）、
`ezdxf`（DWG）、`pdfplumber`（PDF 取数）、`xarray`/`netCDF4`/`geopandas`（气象与地理）。
装包只走镜像：`-i https://pypi.tuna.tsinghua.edu.cn/simple`。

## 2. 排版工具链

无 LaTeX、无 MATLAB、无 R、无 LibreOffice、无 Microsoft Word。
→ **论文只能 Word/WPS 路线**，公式在 Word 里排，最终导出 PDF 提交。
→ `format2025.doc` 这类老式二进制 `.doc` **无法程序解析**，需人工用 WPS 另存为 `.docx`
   后由 `python-docx` 读取。

## 3. 网络实测

- 国内镜像可用：清华源、PyPI、ModelScope 均通。
- **GitHub 不可靠**：2026-09-22 晚 `git push` 连续三次 `Failed to connect to github.com:443`，
  `ls-remote` 成功过一次后全失败。本机无代理、无代理监听端口。
- 结论：**三个人之间的同步不得依赖远程仓库**。顺序为
  ① 本地 git 管回滚与 diff（已可用）② 交接包打 zip 走网盘/局域网 ③ 远程只作备份，推不上不阻塞。
- **明天真实赛题的原文与附件禁止推入仓库**（`.gitignore` 已排除 `data/raw`、`data/processed`）。

## 4. GPU（2026-09-22 晚实测，`dryrun/3-5-冒烟.py` + warmup 复测）

RTX 5060 Ti，**15.9 GB 显存可用**，`torch.cuda.is_available() == True`。

| 项 | 实测 |
|---|---|
| 视频解码 | `cv2.VideoCapture` 读 2025 高教社杯 E 题 mp4 成功：1280×720@30fps、301 帧 |
| 稳态算力参考 | 720p 单帧单层 `Conv2d(3,64,3)`：**2.83 ms/次**（warmup 30 次后测 200 次） |
| 冷启动参考 | 未 warmup 时 **19.3 ms/次**，比稳态慢 6.8 倍 |
| 峰值显存 | 689 MB（冷）/ 473 MB（稳态批次 1） |
| 单段视频粗估 | 301 帧过该层约 0.9 s，未计解码耗时 |

结论与注意：
1. **明天的 DL/CV 路线可用**，视频类题在本机可跑；16 GB 显存对单段 720p 逐帧处理余量充足。
2. **任何耗时估算必须先 warmup 再测**。冷启动会把吞吐低估近 7 倍，据此判断"跑不动"从而回避某类题，是今晚实测到的真实陷阱。
3. 计时时记得 `torch.cuda.synchronize()`——CUDA 是异步的，不同步测出来的墙钟时间是假的。
4. 在以上实测之外，**不要把"能跑大模型"当成选题依据**：能跑得动 720p 逐帧卷积，不等于能在一夜之间训出一个能拿分的分割模型。


## 5. 环境冻结规则

**环境一旦能跑就冻结。**明早不得因为"想试试某个新模型"而改动 torch/cuda 相关包。
新增依赖只允许是纯 Python 包，且装完立刻在此表登记版本。

## 6. 脚本用法与退出码

全部在 `scaffold/scripts/`，退出码统一：`0` 通过、`1` 判据不通过、`2` 脚本自身异常。

```bash
PY=/f/anaconda/envs/ptg/python.exe
$PY scaffold/scripts/bootstrap.py      <工作区> <小问数>    # 建目录与六份事实源空壳
$PY scaffold/scripts/check_structure.py <工作区>            # V1 结构验收
$PY scaffold/scripts/check_numbers.py   <工作区> [0.95]     # V3-1 数字台账引用率
$PY scaffold/scripts/run_all.py         <工作区>            # V0-3 一键复现
$PY scaffold/scripts/coldstart.py       <工作区> [题面.txt] # V0-1 冷启动输入打包
$PY scaffold/scripts/env_lock.py        <工作区>            # V2-6 环境快照
$PY scaffold/scripts/numbers_add.py     <工作区> <值> <单位> <来源脚本> <出现位置> <复算方式>
$PY scaffold/scripts/issue_add.py       <工作区> <定位> <类别> <影响面> <假设> <验证> <优先级> <复现命令> <owner>
$PY -m pytest tests -q                                      # 脚本自测，当前 29 passed
```

`numbers_add.py` 会拒绝来源脚本不存在的登记；`issue_add.py` 会拒绝没有复现命令、
没有 owner 的登记。**这不是麻烦，这是"未登记的瑕疵是事故"这条规矩在代码里的形状。**
