#!/usr/bin/env python3
"""
This module contains a benchmark runner which is used for reporting the findings
in the paper associated with this codebase.

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
            Path("tests/leapfrog_benchmarks/datacenter/switch.p4"),
            Path("tests/leapfrog_benchmarks/datacenter/switch.p4"),
        ),
        Benchmark(
            "edge_self",
            Path("tests/leapfrog_benchmarks/edge/plain.p4"),
            Path("tests/leapfrog_benchmarks/edge/plain.p4"),
        ),
        Benchmark(
            "edge_optimised",
            Path("tests/leapfrog_benchmarks/edge/plain.p4"),
            Path("tests/leapfrog_benchmarks/edge/optimised.p4"),
        ),
        Benchmark(
            "enterprise",
            Path("tests/leapfrog_benchmarks/enterprise/router.p4"),
            Path("tests/leapfrog_benchmarks/enterprise/router.p4"),
        ),
        Benchmark(
            "external_filtering",
            Path("tests/leapfrog_benchmarks/external_filtering/sloppy.p4"),
            Path("tests/leapfrog_benchmarks/external_filtering/strict.p4"),
        ),
        # Benchmark(
        #     "header_initialisation",
        #     Path("tests/leapfrog_benchmarks/header_initialisation/read_initialised.p4"),
        #     Path(
        #         "tests/leapfrog_benchmarks/header_initialisation/read_uninitialised.p4"
        #     ),
        # ),
        Benchmark(
            "service_provider",
            Path("tests/leapfrog_benchmarks/service_provider/core_router.p4"),
            Path("tests/leapfrog_benchmarks/service_provider/core_router.p4"),
        ),
        Benchmark(
            "speculative_extraction",
            Path("tests/leapfrog_benchmarks/speculative_extraction/mpls.p4"),
            Path("tests/leapfrog_benchmarks/speculative_extraction/mpls_vectorised.p4"),
        ),
        Benchmark(
            "state_rearrangement",
            Path("tests/leapfrog_benchmarks/state_rearrangement/combined_states.p4"),
            Path("tests/leapfrog_benchmarks/state_rearrangement/separate_states.p4"),
        ),
        Benchmark(
            "variable_length_formats",
            Path("tests/leapfrog_benchmarks/variable_length_formats/ipoptions.p4"),
            Path("tests/leapfrog_benchmarks/variable_length_formats/timestamp.p4"),
        ),
    ]


def get_all_run_variants() -> List[BenchmarkRun]:
    return [
        BenchmarkRun("octopus_default", {}),
        BenchmarkRun("octopus_no_leaps", {"disable_leaps": True}),
        BenchmarkRun("octopus_z3", {"solvers": ["z3"]}),
        BenchmarkRun("octopus_cvc5", {"solvers": ["cvc5"]}),
    ]


def run_benchmarks(
    benchmarks: List[Benchmark],
    variants: List[BenchmarkRun],
    output_file: str | None = None,
) -> List[str]:
    result = []

    with tempfile.NamedTemporaryFile(mode="w", delete=True) as tmp_output:
        output_path = tmp_output.name

        output_stream = None
        if output_file:
            try:
                output_stream = open(output_file, "w", encoding="utf-8")
            except OSError:
                sys.exit(1)

        def emit(line: str):
            result.append(line)
            if output_stream:
                output_stream.write(f"{line}\n")
                output_stream.flush()
            else:
                print(line, flush=True)

        for variant in tqdm(variants, desc="Variants"):
            emit(f"Running variant: {variant.name}")
            for benchmark in tqdm(
                benchmarks, desc=f"Benchmarks ({variant.name})", leave=False
            ):
                avg_time = run_benchmark(benchmark, variant, output_path)
                emit(f"{benchmark.name} ({variant.name}): {avg_time:.3f} seconds")

        if output_stream:
            output_stream.close()

    return result


def run_benchmark(benchmark: Benchmark, variant: BenchmarkRun, output_path) -> float:
    times = []
    for i in range(RUNS_PER_BENCHMARK):
        cmd = TIME_CMD + [
            "python3",
            "-m",
            "octopus.main",
            "--output",
            output_path,
        ]

        if variant.arguments.get("disable_leaps"):
            cmd.append("--disable_leaps")

        solvers = variant.arguments.get("solvers")
        if solvers:
            cmd.extend(["--solvers", str(solvers)])

        cmd.extend(
            [
                str(benchmark.file1),
                str(benchmark.file2),
            ]
        )

        result = subprocess.run(
            cmd,
            stderr=subprocess.PIPE,
            stdout=sys.stdout,
            text=True,
            shell=False,
        )

        match = re.search(
            r"Elapsed \(wall clock\) time.*?:\s*(\d+):(\d+(?:\.\d+)?)",
            result.stderr,
        )
        print(result.stderr)
        if match:
            minutes = int(match.group(1))
            seconds = float(match.group(2))
            if i > 3:
                times.append(minutes * 60 + seconds)
    return statistics.mean(times)


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

    if len(selected_benchmarks) == 0 or len(selected_variants) == 0:
        print("No benchmarks or variants selected. Exiting.")
        sys.exit(1)

    run_benchmarks(selected_benchmarks, selected_variants, args.output)

if __name__ == "__main__":
    main()
