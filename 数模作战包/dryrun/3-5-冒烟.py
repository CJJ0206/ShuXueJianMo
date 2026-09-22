"""今晚专用：验证明天 DL/CV 路线的地基。不求解任何题。"""
import glob
import sys
import time

import cv2
import torch

print("torch", torch.__version__, "| cuda available:", torch.cuda.is_available())
if not torch.cuda.is_available():
    print("[FAIL] CUDA 不可用——明天必须走 CPU 路线，并相应下调模型规模预期")
    sys.exit(1)
print("device:", torch.cuda.get_device_name(0),
      "| 显存", round(torch.cuda.get_device_properties(0).total_memory / 1024 ** 3, 1), "GB")

vids = glob.glob(r"C:/Users/Administrator/Desktop/CUMCM2025Problems/E题/附件/附件1/*.mp4")
print("找到视频数:", len(vids))
if not vids:
    print("[FAIL] 夹具视频不在，冒烟测试无法执行")
    sys.exit(1)

cap = cv2.VideoCapture(vids[0])
ok, frame = cap.read()
fps = cap.get(cv2.CAP_PROP_FPS)
nfr = cap.get(cv2.CAP_PROP_FRAME_COUNT)
print(f"首帧 ok={ok} shape={None if frame is None else frame.shape} fps={fps:.2f} 帧数={nfr:.0f}")
cap.release()
assert ok and frame is not None, "cv2 读不到 mp4——明天视频类题不可行，必须提前知道"

t = time.time()
x = torch.from_numpy(frame).permute(2, 0, 1).float().unsqueeze(0) / 255.0
x = x.cuda()
conv = torch.nn.Conv2d(3, 64, 3, padding=1).cuda()
for _ in range(20):
    y = torch.relu(conv(x))
torch.cuda.synchronize()
ms = (time.time() - t) * 1000
peak = torch.cuda.max_memory_allocated() / 1024 ** 2
print(f"单帧 20 次 conv 耗时 {ms:.1f} ms | 峰值显存 {peak:.0f} MB")
assert y.shape[1] == 64, "输出通道数异常"
print(f"SMOKE PASS | 结论：明天可走 DL/CV 路线；粗估 {(ms / 20):.1f} ms/帧/层组")
