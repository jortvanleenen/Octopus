#!/usr/bin/env python3
"""
This module contains a benchmark runner which is used for reporting the findings
in the paper associated with this codebase.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import subprocess
import statistics
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Any
import sys
import tempfile
import re

from tqdm import tqdm

RUNS_PER_BENCHMARK = 5
TIME_CMD = ["/usr/bin/time", "-v"]


@dataclass(frozen=True)
class Benchmark:
    name: str
    file1: Path
    file2: Path


@dataclass(frozen=True)
class BenchmarkRun:
    name: str
    arguments: dict[str, Any]


def get_all_benchmarks() -> List[Benchmark]:
    return [
        Benchmark(
            "datacenter",
            Path("leapfrog_benchmarks/datacenter/switch.p4"),
            Path("leapfrog_benchmarks/datacenter/switch.p4"),
        ),
        Benchmark(
            "edge_self",
            Path("leapfrog_benchmarks/edge/plain.p4"),
            Path("leapfrog_benchmarks/edge/plain.p4"),
        ),
        Benchmark(
            "edge_optimised",
            Path("leapfrog_benchmarks/edge/plain.p4"),
            Path("leapfrog_benchmarks/edge/optimised.p4"),
        ),
        Benchmark(
            "edge_compiled",
            Path("leapfrog_benchmarks/edge/plain.p4"),
            Path("leapfrog_benchmarks/edge/compiled.p4"),
        ),
        Benchmark(
            "enterprise",
            Path("leapfrog_benchmarks/enterprise/router.p4"),
            Path("leapfrog_benchmarks/enterprise/router.p4"),
        ),
        Benchmark(
            "external_filtering",
            Path("leapfrog_benchmarks/external_filtering/sloppy.p4"),
            Path("leapfrog_benchmarks/external_filtering/strict.p4"),
        ),
        Benchmark(
            "header_initialisation",
            Path("leapfrog_benchmarks/header_initialisation/read_initialised.p4"),
            Path("leapfrog_benchmarks/header_initialisation/read_uninitialised.p4"),
        ),
        Benchmark(
            "service_provider_self",
            Path("leapfrog_benchmarks/service_provider/plain.p4"),
            Path("leapfrog_benchmarks/service_provider/plain.p4"),
        ),
        Benchmark(
            "service_provider_compiled",
            Path("leapfrog_benchmarks/service_provider/plain.p4"),
            Path("leapfrog_benchmarks/service_provider/compiled.p4"),
        ),
        Benchmark(
            "speculative_extraction",
            Path("leapfrog_benchmarks/speculative_extraction/mpls.p4"),
            Path("leapfrog_benchmarks/speculative_extraction/mpls_vectorised.p4"),
        ),
        Benchmark(
            "state_rearrangement",
            Path("leapfrog_benchmarks/state_rearrangement/combined_states.p4"),
            Path("leapfrog_benchmarks/state_rearrangement/seperate_states.p4"),
        ),
        Benchmark(
            "variable_length_formats",
            Path("leapfrog_benchmarks/variable_length_formats/ipoptions.p4"),
            Path("leapfrog_benchmarks/variable_length_formats/timestamp.p4"),
        ),
    ]


def get_all_run_variants() -> List[BenchmarkRun]:
    return [
        BenchmarkRun("leapfrog_comparison", {"solvers": ["Z3", "cvc4"]}),
        BenchmarkRun("octopus_default", {}),
        BenchmarkRun("octopus_no_leaps", {"disable_leaps": True}),
        BenchmarkRun("octopus_z3", {"solvers": ["Z3"]}),
        BenchmarkRun("octopus_cvc5", {"solvers": ["cvc5"]}),
    ]


def run_benchmark(benchmark: Benchmark, variant: BenchmarkRun) -> float:
    times = []
    for i in tqdm(
        range(RUNS_PER_BENCHMARK + 1), desc=f"{benchmark.name} runs", leave=False
    ):
        args = {
            "file1": str(benchmark.file1),
            "file2": str(benchmark.file2),
            "json": True,
            "verbosity": 0,
            "naive": False,
            "disable_leaps": variant.arguments.get("disable_leaps", False),
            "solvers": str(variant.arguments.get("solvers", ["z3", "cvc5"])),
            "solvers_global_options": None,
            "output": None,
            "fail_on_mismatch": False,
            "stat": False,
        }
        with tempfile.NamedTemporaryFile() as temp_out:
            cmd = (
                TIME_CMD
                + ["python3", "-m", "octopus.main"]
                + [
                    f"--{k}" if isinstance(v, bool) and v else f"--{k}={v}"
                    for k, v in args.items()
                    if v is not False and v is not None
                ]
            )
            result = subprocess.run(
                cmd,
                stderr=subprocess.PIPE,
                stdout=temp_out,
                text=True,
                shell=False,
            )
            match = re.search(
                r"Elapsed \(wall clock\) time.*?:\s*(\d+):(\d+(?:\.\d+)?)",
                result.stderr,
            )
            if match:
                minutes = int(match.group(1))
                seconds = float(match.group(2))
                if i > 3:
                    times.append(minutes * 60 + seconds)
    return statistics.mean(times)


def run_benchmarks(
    benchmarks: List[Benchmark], variants: List[BenchmarkRun]
) -> List[str]:
    result = []
    for variant in tqdm(variants, desc="Variants"):
        result.append(f"Running variant: {variant.name}")
        for benchmark in tqdm(
            benchmarks, desc=f"Benchmarks ({variant.name})", leave=False
        ):
            avg_time = run_benchmark(benchmark, variant)
            result.append(f"{benchmark.name} ({variant.name}): {avg_time:.3f} seconds")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()

    available_benchmark_names = [bench.name for bench in get_all_benchmarks()]
    parser.add_argument(
        "--benchmark",
        nargs="+",
        help="List of benchmarks to run. If not provided, all benchmarks will be run. Available: "
        + ", ".join(available_benchmark_names),
    )

    available_variant_names = [variant.name for variant in get_all_run_variants()]
    parser.add_argument(
        "--variant",
        nargs="+",
        help="List of variants to run. If not provided, all variants will be run. Available: "
        + ", ".join(available_variant_names),
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Write the benchmark results to this file. If not provided, stdout is used",
    )

    args = parser.parse_args()

    all_benchmarks = get_all_benchmarks()
    selected_benchmarks = (
        [b for b in all_benchmarks if b.name in args.benchmark]
        if args.benchmark
        else all_benchmarks
    )

    all_variants = get_all_run_variants()
    selected_variants = (
        [v for v in all_variants if v.name in args.variant]
        if args.variant
        else all_variants
    )

    result = run_benchmarks(selected_benchmarks, selected_variants)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                for res in result:
                    f.write(f"{res}\n")
        except OSError:
            sys.exit(1)
    else:
        for res in result:
            print(res)

if __name__ == "__main__":
    main()