import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator, ScalarFormatter

plt.rcParams.update({
    "axes.titlesize": 20,
    "axes.labelsize": 18,

    "xtick.labelsize": 18,
    "ytick.labelsize": 18,
})

# Raw benchmark output from runner.py
RAW = """
parse_field_1: avg. wall time: 0.41 seconds, avg. max. memory usage: 38.82 MiB
parse_field_4: avg. wall time: 0.41 seconds, avg. max. memory usage: 38.73 MiB
parse_field_16: avg. wall time: 0.41 seconds, avg. max. memory usage: 38.98 MiB
parse_field_64: avg. wall time: 0.48 seconds, avg. max. memory usage: 39.88 MiB

parse_header_4_1: avg. wall time: 0.41 seconds, avg. max. memory usage: 38.90 MiB
parse_header_4_4: avg. wall time: 0.85 seconds, avg. max. memory usage: 39.87 MiB
parse_header_4_16: avg. wall time: 9.59 seconds, avg. max. memory usage: 107.00 MiB
parse_header_4_32: avg. wall time: 56.91 seconds, avg. max. memory usage: 449.85 MiB
parse_header_1_64: avg. wall time: 240.83 seconds, avg. max. memory usage: 1546.22 MiB
parse_header_1_98: avg. wall time: 791.26 seconds, avg. max. memory usage: 5070.01 MiB

parse_complex_2_2: avg. wall time: 1.35 seconds, avg. max. memory usage: 44.45 MiB
parse_complex_2_4: avg. wall time: 11.63 seconds, avg. max. memory usage: 150.67 MiB
parse_complex_2_6: avg. wall time: 68.77 seconds, avg. max. memory usage: 820.28 MiB
parse_complex_3_3: avg. wall time: 38.87 seconds, avg. max. memory usage: 388.47 MiB
parse_complex_3_4: avg. wall time: 245.20 seconds, avg. max. memory usage: 2226.86 MiB
parse_complex_4_2: avg. wall time: 19.01 seconds, avg. max. memory usage: 191.27 MiB
parse_complex_4_3: avg. wall time: 433.07 seconds, avg. max. memory usage: 3650.11 MiB
parse_complex_6_2: avg. wall time: 395.20 seconds, avg. max. memory usage: 3150.97 MiB
"""
# (octopus_default) - benchmark parse_complex_4_4: avg. wall time: 5811.00 seconds, avg. max. memory usage: 41754.00 MiB

# (octopus_default) - benchmark equiv_field_4_and_header_4_1: avg. wall time:
# 0.39 seconds, avg. max. memory usage: 38.90 MiB
# (octopus_default) - benchmark subset_field_4_and_header_4_4: avg. wall time:
#  0.50 seconds, avg. max. memory usage: 39.70 MiB
# (octopus_default) - benchmark subset_field_1_and_complex_3_1: avg. wall time
# : 0.45 seconds, avg. max. memory usage: 39.79 MiB

pattern = re.compile(
    r'parse_(field|header|complex)_(\d+)(?:_(\d+))?:.*?time:\s*([\d.]+).*?usage:\s*([\d.]+)',
    re.IGNORECASE
)

data = {"field": [], "header": [], "complex": []}

for kind, a, b, t, m in pattern.findall(RAW):
    a, t, m = int(a), float(t), float(m)
    b = int(b) if b else None

    if kind == "field":
        x = a
        label = f"{a}"
    elif kind == "header":
        x = b
        label = f"{b}"
    else:
        d, f = a, b
        x = (f ** (d + 1) - 1) / (f - 1)
        label = f"{d},{f}"

    data[kind].append((x, t, m, label))

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

titles = {
    "field": "parse-field",
    "header": "parse-header",
    "complex": "parse-complex (d,f)",
}

x_axes = {
    "field": "#Fields",
    "header": "#Headers",
    "complex": "#States"
}

TIME_COLOUR = "#0C7BDC"  # Blue
MEM_COLOUR = "#FFC20A"  # Orange-ish

for col, kind in enumerate(["field", "header", "complex"]):
    xs = np.array([e[0] for e in data[kind]])
    ts = np.array([e[1] for e in data[kind]])
    ms = np.array([e[2] for e in data[kind]])

    order = np.argsort(xs)
    xs, ts, ms = xs[order], ts[order], ms[order]

    ax_time = axes[col]
    ax_time.set_title(titles[kind], pad=10)
    ax_mem = ax_time.twinx()
    ax_time.set_zorder(2)
    ax_mem.set_zorder(1)
    ax_time.patch.set_visible(False)

    # Time: solid line + circles
    ax_time.plot(xs, ts, linestyle='-', linewidth=2, color=TIME_COLOUR, zorder=3)
    ax_time.scatter(xs, ts, marker='o', color=TIME_COLOUR, zorder=4, s=100)

    # Memory: dashed line + squares
    ax_mem.plot(xs, ms, linestyle='--', linewidth=2, color=MEM_COLOUR, zorder=3)
    ax_mem.scatter(xs, ms, marker='s', color=MEM_COLOUR, zorder=4, s=100)

    ax_time.set_title(titles[kind], fontweight="bold")
    ax_time.set_xlabel(x_axes[kind], fontweight="bold")
    ax_time.set_ylabel("Time (s)", fontweight="bold")
    ax_mem.set_ylabel("Memory (MiB)", fontweight="bold")

    ax_time.set_yscale("linear")
    ax_mem.set_yscale("linear")

    if kind == "field":
        ax_time.set_ylim(bottom=0)

    ax_time.yaxis.set_major_locator(MaxNLocator(nbins=5))
    ax_mem.yaxis.set_major_locator(MaxNLocator(nbins=5))

    formatter = ScalarFormatter()
    formatter.set_scientific(False)
    formatter.set_useOffset(False)
    ax_mem.yaxis.set_major_formatter(formatter)

    ax_time.grid(True, which="both", axis="y", alpha=0.4)

    for x, t, m, lbl in data[kind]:
        if kind == "complex":
            if lbl != "4,3" and lbl != "6,2":
                ax_time.annotate(
                    lbl, (x, t),
                    textcoords="offset points",
                    xytext=(-24, 10),
                    fontsize=16,
                    fontweight="bold",
                    zorder=10
                )
            else:
                ax_time.annotate(
                    lbl, (x, t),
                    textcoords="offset points",
                    xytext=(-40, -2),
                    fontsize=16,
                    fontweight="bold",
                    zorder=10
                )

legend_elements = [
    Line2D([0], [0], marker='o', linestyle='-', color=TIME_COLOUR,
           label='Time', markersize=7),
    Line2D([0], [0], marker='s', linestyle='--', color=MEM_COLOUR,
           label='Memory', markersize=7),
]

fig.legend(
    handles=legend_elements,
    loc="upper center",
    ncol=2,
    frameon=False,
    markerscale=1.4,
    prop={"size": 16, "weight": "bold"}
)

plt.subplots_adjust(
    left=0.06,
    right=0.94,
    top=0.85,
    bottom=0.15,
    wspace=0.5,
)
plt.show()
