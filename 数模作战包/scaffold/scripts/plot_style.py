"""统一 matplotlib 风格（V3-4）。用法：from plot_style import apply, savefig"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def apply():
    plt.rcParams.update({
        "font.sans-serif": ["Microsoft YaHei", "SimHei"],
        "axes.unicode_minus": False,
        "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
        "lines.linewidth": 1.4, "figure.dpi": 120, "savefig.dpi": 300,
        "axes.grid": True, "grid.alpha": 0.3,
        # 灰度可辨：靠明度差而非色相区分系列
        "axes.prop_cycle": plt.cycler(color=["#111111", "#666666", "#999999",
                                             "#333333", "#777777", "#BBBBBB"]),
    })


def savefig(fig, path):
    """双份输出：pdf 供排版，png 供预览。返回两个路径。"""
    stem = str(path).rsplit(".", 1)[0]
    fig.savefig(stem + ".pdf", bbox_inches="tight")
    fig.savefig(stem + ".png", bbox_inches="tight")
    return stem + ".pdf", stem + ".png"
