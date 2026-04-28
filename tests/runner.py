#!/usr/bin/env python3
"""
This module contains a benchmark runner which is used for reporting the
Leapfrog and Whippersnapper findings.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import argparse
import re
import statistics
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator, ScalarFormatter
from tqdm import tqdm

plt.rcParams.update({
    "axes.titlesize": 20,
    "axes.labelsize": 18,
    "xtick.labelsize": 18,
    "ytick.labelsize": 18,
})

RUNS_PER_BENCHMARK = 3
TIME_CMD = ["/usr/bin/time", "-v"]

GEN_RE = re.compile(r"\[TIMING]\s*generation=(\d+\.\d+)")
VAL_RE = re.compile(r"\[TIMING]\s*validation=(\d+\.\d+)")
MEM_RE = re.compile(r"Maximum resident set size .*?:\s*(\d+)")


@dataclass(frozen=True)
class Benchmark:
    """A dataclass representing a benchmark, consisting of a name and two P4 files."""

    name: str
    file1: Path
    file2: Path
    arguments: dict[str, Any] = None


@dataclass(frozen=True)
class BenchmarkRun:
    """A dataclass representing the run of one or more benchmarks with a set of arguments."""

    name: str
    arguments: dict[str, Any]


def get_leapfrog_benchmarks() -> List[Benchmark]:
    """
    Get the Leapfrog benchmarks that are used in the paper.

    :return: a list of Benchmark objects representing the benchmarks
    """
    return [
        Benchmark(
            "state_rearrangement",
            Path("tests/leapfrog_benchmarks/state_rearrangement/combined_states.p4"),
            Path("tests/leapfrog_benchmarks/state_rearrangement/separate_states.p4"),
        ),
        Benchmark(
            "variable_length_formats_2",
            Path("tests/leapfrog_benchmarks/variable_length_formats_2/ipoptions.p4"),
            Path("tests/leapfrog_benchmarks/variable_length_formats_2/timestamp.p4"),
        ),
        Benchmark(
            "variable_length_formats_3",
            Path("tests/leapfrog_benchmarks/variable_length_formats_3/ipoptions.p4"),
            Path("tests/leapfrog_benchmarks/variable_length_formats_3/timestamp.p4"),
        ),
        Benchmark(
            "header_initialization",
            Path("tests/leapfrog_benchmarks/header_initialisation/correct.p4"),
            Path("tests/leapfrog_benchmarks/header_initialisation/correct.p4"),
        ),
        Benchmark(
            "speculative_extraction",
            Path("tests/leapfrog_benchmarks/speculative_extraction/mpls.p4"),
            Path("tests/leapfrog_benchmarks/speculative_extraction/mpls_vectorised.p4"),
        ),
        Benchmark(
            "relational_verification",
            Path("tests/leapfrog_benchmarks/external_filtering/sloppy.p4"),
            Path("tests/leapfrog_benchmarks/external_filtering/strict.p4"),
            arguments={
                "filter-accepting-string":
                    "((hdr_l.hdr.eth.data[15:0] == '0x8600_16' and hdr_l.hdr.ipv4.data == hdr_r.hdr.ipv4.data) "
                    "or (hdr_l.hdr.eth.data[15:0] == '0x86dd_16' and hdr_l.hdr.ipv6.data == hdr_r.hdr.ipv6.data))",
                "filter-disagreeing-string": "True",
            },
        ),
        Benchmark(
            "external_filtering",
            Path("tests/leapfrog_benchmarks/external_filtering/sloppy.p4"),
            Path("tests/leapfrog_benchmarks/external_filtering/strict.p4"),
            arguments={
                "filter-disagreeing-string":
                    "hdr_r.hdr.eth.data[15:0] != '0x8600_16' and hdr_r.hdr.eth.data[15:0] != '0x86dd_16'"},
        ),
        Benchmark(
            "edge",
            Path("tests/leapfrog_benchmarks/edge/plain.p4"),
            Path("tests/leapfrog_benchmarks/edge/plain.p4"),
        ),
        Benchmark(
            "service_provider",
            Path("tests/leapfrog_benchmarks/service_provider/core_router.p4"),
            Path("tests/leapfrog_benchmarks/service_provider/core_router.p4"),
        ),
        Benchmark(
            "datacenter",
            Path("tests/leapfrog_benchmarks/datacenter/switch.p4"),
            Path("tests/leapfrog_benchmarks/datacenter/switch.p4"),
        ),
        Benchmark(
            "enterprise",
            Path("tests/leapfrog_benchmarks/enterprise/router.p4"),
            Path("tests/leapfrog_benchmarks/enterprise/router.p4"),
        ),
        Benchmark(
            "translation_validation",
            Path("tests/leapfrog_benchmarks/edge/plain.p4"),
            Path("tests/leapfrog_benchmarks/edge/optimised.p4"),
        ),
    ]


def get_whippersnapper_benchmarks() -> List[Benchmark]:
    """
    Get the Whippersnapper benchmarks that are used in the paper.

    :return: a list of Benchmark objects representing the benchmarks
    """
    return [
        Benchmark(
            "parse_field_1",
            Path("tests/whippersnapper/parse-field/1.p4"),
            Path("tests/whippersnapper/parse-field/1.p4"),
        ),
        Benchmark(
            "parse_field_4",
            Path("tests/whippersnapper/parse-field/4.p4"),
            Path("tests/whippersnapper/parse-field/4.p4"),
        ),
        Benchmark(
            "parse_field_16",
            Path("tests/whippersnapper/parse-field/16.p4"),
            Path("tests/whippersnapper/parse-field/16.p4"),
        ),
        Benchmark(
            "parse_field_64",
            Path("tests/whippersnapper/parse-field/64.p4"),
            Path("tests/whippersnapper/parse-field/64.p4"),
        ),
        Benchmark(
            "parse_header_4_1",
            Path("tests/whippersnapper/parse-header/4-1.p4"),
            Path("tests/whippersnapper/parse-header/4-1.p4"),
        ),
        Benchmark(
            "parse_header_4_4",
            Path("tests/whippersnapper/parse-header/4-4.p4"),
            Path("tests/whippersnapper/parse-header/4-4.p4"),
        ),
        Benchmark(
            "parse_header_4_16",
            Path("tests/whippersnapper/parse-header/4-16.p4"),
            Path("tests/whippersnapper/parse-header/4-16.p4"),
        ),
        Benchmark(
            "parse_header_4_32",
            Path("tests/whippersnapper/parse-header/4-32.p4"),
            Path("tests/whippersnapper/parse-header/4-32.p4"),
        ),
        Benchmark(
            "parse_header_1_64",
            Path("tests/whippersnapper/parse-header/1-64.p4"),
            Path("tests/whippersnapper/parse-header/1-64.p4"),
        ),
        Benchmark(
            "parse_header_1_98",
            Path("tests/whippersnapper/parse-header/1-98.p4"),
            Path("tests/whippersnapper/parse-header/1-98.p4"),
        ),
        Benchmark(
            "parse_complex_2_2",
            Path("tests/whippersnapper/parse-complex/2-2.p4"),
            Path("tests/whippersnapper/parse-complex/2-2.p4"),
        ),
        Benchmark(
            "parse_complex_2_4",
            Path("tests/whippersnapper/parse-complex/2-4.p4"),
            Path("tests/whippersnapper/parse-complex/2-4.p4"),
        ),
        Benchmark(
            "parse_complex_2_6",
            Path("tests/whippersnapper/parse-complex/2-6.p4"),
            Path("tests/whippersnapper/parse-complex/2-6.p4"),
        ),
        Benchmark(
            "parse_complex_3_3",
            Path("tests/whippersnapper/parse-complex/3-3.p4"),
            Path("tests/whippersnapper/parse-complex/3-3.p4"),
        ),
        Benchmark(
            "parse_complex_3_4",
            Path("tests/whippersnapper/parse-complex/3-4.p4"),
            Path("tests/whippersnapper/parse-complex/3-4.p4"),
        ),
        Benchmark(
            "parse_complex_4_2",
            Path("tests/whippersnapper/parse-complex/4-2.p4"),
            Path("tests/whippersnapper/parse-complex/4-2.p4"),
        ),
        Benchmark(
            "parse_complex_4_3",
            Path("tests/whippersnapper/parse-complex/4-3.p4"),
            Path("tests/whippersnapper/parse-complex/4-3.p4"),
        ),
        Benchmark(
            "parse_complex_6_2",
            Path("tests/whippersnapper/parse-complex/6-2.p4"),
            Path("tests/whippersnapper/parse-complex/6-2.p4"),
        ),
    ]


def get_whippersnapper_equiv_benchmarks() -> List[Benchmark]:
    """
    Get the Whippersnapper benchmarks that check for non-trivial equivalences
    among the generated parsers.

    :return: a list of Benchmark objects representing the equivalence checks
    """
    return [
        Benchmark(
            "equiv_field_4_and_header_4_1",
            Path("tests/whippersnapper/parse-field/4.p4"),
            Path("tests/whippersnapper/parse-header/4-1.p4"),
        ),
        Benchmark(
            "subset_field_4_and_header_4_4",
            Path("tests/whippersnapper/parse-field/4.p4"),
            Path("tests/whippersnapper/parse-header/4-4.p4"),
            arguments={
                "filter-disagreeing-string":
                    "hdr_r.hdr.header_0.field_0 != '0_16'",
            }
        ),
        Benchmark(
            "subset_field_1_and_complex_3_1",
            Path("tests/whippersnapper/parse-field/1.p4"),
            Path("tests/whippersnapper/parse-complex/3-1.p4"),
            arguments={
                "filter-disagreeing-string":
                    "hdr_r.hdr.ptp.reserved2 == '1_8'",
            }
        ),
    ]


def get_all_run_variants() -> List[BenchmarkRun]:
    """
    Get all variants of the benchmark runs that are used in the paper.

    :return: a list of BenchmarkRun objects representing the variants
    """
    return [
        BenchmarkRun("octopus_default", {}),
    ]


def run_benchmark(benchmark: Benchmark, variant: BenchmarkRun, tmp_path: str, pbar=None):
    gen_times = []
    val_times = []
    memory = []

    for i in range(RUNS_PER_BENCHMARK):
        if pbar:
            run_idx = i + 1
            pbar.set_postfix_str(f"{benchmark.name} ({run_idx}/{RUNS_PER_BENCHMARK})")

        cmd = TIME_CMD + [
            "python3", "-m", "octopus.main",
            "--no-conclusion",
            "--time",
            "--output", tmp_path
        ]

        if variant.arguments:
            for k, v in variant.arguments.items():
                cmd.extend([f"--{k}", str(v)])

        if benchmark.arguments:
            for k, v in benchmark.arguments.items():
                cmd.extend([f"--{k}", str(v)])

        cmd.extend([str(benchmark.file1), str(benchmark.file2)])

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        out = result.stdout
        err = result.stderr

        g = GEN_RE.search(out)
        v = VAL_RE.search(out)
        m = MEM_RE.search(err)
        if not g or not m or (not v and "no-validation" not in variant.arguments.keys()):
            raise RuntimeError(
                f"Failed to parse timing/memory output for benchmark {benchmark.name} (variant {variant.name}):\n"
                f"stdout:\n{out}\nstderr:\n{err}"
            )
        gen_times.append(float(g.group(1)))
        memory.append((int(m.group(1)) * 1000) / (1024 ** 2))
        if v:
            val_times.append(float(v.group(1)))

        if pbar:
            pbar.update(1)

    return (
        statistics.mean(gen_times),
        statistics.mean(val_times),
        statistics.mean(memory),
    )


def run_leapfrog(benchmarks, variants):
    for variant in variants:
        results = []

        total = len(benchmarks) * RUNS_PER_BENCHMARK

        with tempfile.NamedTemporaryFile() as tmp:
            with tqdm(total=total, desc="Leapfrog equiv. checks") as pbar:
                for b in benchmarks:
                    gen, val, mem = run_benchmark(b, variant, tmp.name, pbar)
                    results.append((b.name, gen, val, mem))

        print(f"\n=== {variant.name} ===")
        print(f"{'Benchmark':<35} {'Gen (s)':>10} {'Val (s)':>10} {'Mem (MiB)':>12}")
        print("-" * 70)
        for name, gen, val, mem in results:
            print(f"{name:<35} {gen:>10.4f} {val:>10.4f} {mem:>12.2f}")


def run_whippersnapper(benchmarks, variants):
    results = []

    total = len(benchmarks) * RUNS_PER_BENCHMARK

    with tempfile.NamedTemporaryFile() as tmp:
        with tqdm(total=total, desc="Whippersnapper equiv. checks") as pbar:
            for variant in variants:
                for b in benchmarks:
                    gen, val, mem = run_benchmark(b, variant, tmp.name, pbar)
                    total_time = gen + val
                    results.append((b.name, gen, total_time, mem))

    plot(results)


def run_whippersnapper_equiv(benchmarks, variants):
    for variant in variants:
        results = []

        with tempfile.NamedTemporaryFile() as tmp:
            with tqdm(total=len(benchmarks), desc="Whippersnapper equiv. checks") as pbar:
                for b in benchmarks:
                    pbar.set_postfix_str(b.name)

                    cmd = [
                        "python3", "-m", "octopus.main",
                        "--no-conclusion",
                        "--output", tmp.name
                    ]

                    if variant.arguments:
                        for k, v in variant.arguments.items():
                            cmd.extend([f"--{k}", str(v)])

                    if b.arguments:
                        for k, v in b.arguments.items():
                            cmd.extend([f"--{k}", str(v)])

                    cmd.extend([str(b.file1), str(b.file2)])

                    result = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )

                    success = (result.returncode == 0)
                    results.append((b.name, success))

                    pbar.update(1)

        print(f"\n=== {variant.name} ===")
        for name, success in results:
            status = "found equivalent" if success else "NOT found equivalent"
            print(f"{name}: {status}")


def plot(results):
    data = {"field": [], "header": [], "complex": []}
    pattern = re.compile(r'parse_(field|header|complex)_(\d+)(?:_(\d+))?')

    for name, gen, total, m in results:
        match = pattern.match(name)
        if not match:
            continue

        kind, a, b = match.groups()
        a = int(a)
        b = int(b) if b else None

        if kind == "field":
            x = a
            label = str(a)
        elif kind == "header":
            x = b
            label = str(b)
        else:
            d, f = a, b
            x = (f ** (d + 1) - 1) / (f - 1)
            label = f"{d},{f}"

        data[kind].append((x, gen, total, m, label))

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

    TIME_COLOUR = "#0C7BDC"
    MEM_COLOUR = "#FFC20A"

    for col, kind in enumerate(["field", "header", "complex"]):
        if not data[kind]:
            continue

        xs = np.array([e[0] for e in data[kind]])
        gen_ts = np.array([e[1] for e in data[kind]])
        total_ts = np.array([e[2] for e in data[kind]])
        ms = np.array([e[3] for e in data[kind]])

        order = np.argsort(xs)
        xs, gen_ts, total_ts, ms = xs[order], gen_ts[order], total_ts[order], ms[order]

        ax_time = axes[col]
        ax_mem = ax_time.twinx()

        ax_time.set_zorder(1)
        ax_mem.set_zorder(0)
        ax_time.patch.set_visible(False)

        ax_time.plot(xs, gen_ts, linestyle='-', linewidth=2,
                     color=TIME_COLOUR, zorder=3)
        ax_time.scatter(xs, gen_ts, marker='o',
                        color=TIME_COLOUR, zorder=4, s=100)

        ax_time.plot(xs, total_ts, linestyle='--', linewidth=2,
                     color=TIME_COLOUR, zorder=3)
        ax_time.scatter(xs, total_ts, marker='x',
                        color=TIME_COLOUR, zorder=4, s=100)

        ax_mem.plot(xs, ms, linestyle='--', linewidth=2,
                    color=MEM_COLOUR, zorder=3)
        ax_mem.scatter(xs, ms, marker='s',
                       color=MEM_COLOUR, zorder=4, s=100)

        ax_time.set_title(titles[kind], fontweight="bold", pad=10)
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

        ax_time.set_axisbelow(True)
        ax_time.grid(True, which="both", axis="y",
                     linewidth=0.3, color="#CCCCCC", zorder=0)
        for x, gen, total, m, lbl in data[kind]:
            if kind == "complex":
                if lbl not in {"4,3", "6,2"}:
                    offset = (-24, 10)
                else:
                    offset = (-40, -2)

                ax_time.annotate(
                    lbl, (x, total),
                    textcoords="offset points",
                    xytext=offset,
                    fontsize=16,
                    fontweight="bold",
                    zorder=10
                )

    legend_elements = [
        Line2D([0], [0], marker='o', linestyle='-',
               color=TIME_COLOUR, label='Generation time', markersize=7),
        Line2D([0], [0], marker='x', linestyle='--',
               color=TIME_COLOUR, label='Total time (gen+val)', markersize=7),
        Line2D([0], [0], marker='s', linestyle='--',
               color=MEM_COLOUR, label='Memory', markersize=7),
    ]

    fig.legend(
        handles=legend_elements,
        loc="upper center",
        ncol=2,
        frameon=False,
        markerscale=1.4,
        prop={"size": 16, "weight": "bold"}
    )

    plt.tight_layout(rect=[0, 0, 1, 0.88])

    plt.savefig("whippersnapper_plot.png", dpi=300)
    plt.close()


def main() -> None:
    """Entry point of the benchmark runner."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--suite",
        choices=["leapfrog", "whippersnapper", "whippersnapper_equiv"],
        required=True,
    )
    parser.add_argument("--benchmark", nargs="+")
    parser.add_argument("--variant", nargs="+")

    args = parser.parse_args()

    if args.suite == "leapfrog":
        all_benchmarks = get_leapfrog_benchmarks()
    elif args.suite == "whippersnapper":
        all_benchmarks = get_whippersnapper_benchmarks()
    elif args.suite == "whippersnapper_equiv":
        all_benchmarks = get_whippersnapper_equiv_benchmarks()
    else:
        raise ValueError(f"Unknown suite: {args.suite}")

    if args.benchmark:
        selected_benchmarks = [b for b in all_benchmarks if b.name in args.benchmark]
        invalid = set(args.benchmark) - {b.name for b in all_benchmarks}
        if invalid:
            print(f"Unknown benchmarks: {invalid}")
            sys.exit(1)
    else:
        selected_benchmarks = all_benchmarks

    all_variants = get_all_run_variants()
    if args.variant:
        selected_variants = [v for v in all_variants if v.name in args.variant]
        invalid = set(args.variant) - {v.name for v in all_variants}
        if invalid:
            print(f"Unknown variants: {invalid}")
            sys.exit(1)
    else:
        selected_variants = all_variants

    if not selected_benchmarks:
        print("No benchmarks selected")
        sys.exit(1)

    if not selected_variants:
        print("No variants selected")
        sys.exit(1)

    if args.suite == "leapfrog":
        run_leapfrog(selected_benchmarks, selected_variants)
    elif args.suite == "whippersnapper":
        run_whippersnapper(selected_benchmarks, selected_variants)
    elif args.suite == "whippersnapper_equiv":
        run_whippersnapper_equiv(selected_benchmarks, selected_variants)


if __name__ == "__main__":
    main()
