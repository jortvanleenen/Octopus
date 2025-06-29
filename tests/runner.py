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
from io import TextIOWrapper
from pathlib import Path
from typing import Any, List

from tqdm import tqdm

RUNS_PER_BENCHMARK = 3
TIME_CMD = ["/usr/bin/time", "-v"]


@dataclass(frozen=True)
class Benchmark:
    """A dataclass representing a benchmark, consisting of a name and two P4 files."""

    name: str
    file1: Path
    file2: Path


@dataclass(frozen=True)
class BenchmarkRun:
    """A dataclass representing the run of one or more benchmarks with a set of arguments."""

    name: str
    arguments: dict[str, Any]


def get_all_benchmarks() -> List[Benchmark]:
    """
    Get all benchmarks that are used in the paper.

    :return: a list of Benchmark objects representing the benchmarks
    """
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
        # Benchmark(
        #     "extended_syntax",
        #     Path("tests/correct_cases/extended_syntax/mpls_default.p4"),
        #     Path("tests/correct_cases/extended_syntax/mpls_extended.p4"),
        # ),
        # Benchmark(
        #     "external_filtering",
        #     Path("tests/leapfrog_benchmarks/external_filtering/sloppy.p4"),
        #     Path("tests/leapfrog_benchmarks/external_filtering/strict.p4"),
        # ),
        Benchmark(
            "header_initialisation_correct",
            Path("tests/leapfrog_benchmarks/header_initialisation/correct.p4"),
            Path("tests/leapfrog_benchmarks/header_initialisation/correct.p4"),
        ),
        # Benchmark(
        #     "header_initialisation_incorrect",
        #     Path("tests/leapfrog_benchmarks/header_initialisation/incorrect.p4"),
        #     Path(
        #         "tests/leapfrog_benchmarks/header_initialisation/incorrect.p4"
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
    """
    Get all variants of the benchmark runs that are used in the paper.

    :return: a list of BenchmarkRun objects representing the variants
    """
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
) -> None:
    """
    Run the benchmarks with the given variants and output the results.

    :param benchmarks: the selected benchmarks to run
    :param variants: the selected variants to run
    :param output_file: the file to write the output to, or None for stdout
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=True) as tmp_output:
        tmp_path = tmp_output.name

        output_stream = None
        if output_file:
            try:
                output_stream = open(output_file, "w", encoding="utf-8")
            except OSError:
                sys.exit(1)

        for variant in tqdm(variants, desc="Variants"):
            for benchmark in tqdm(benchmarks, desc="Benchmarks", leave=False):
                run_benchmark(benchmark, variant, output_stream, tmp_path)

        if output_stream:
            output_stream.close()


def run_benchmark(
    benchmark: Benchmark,
    variant: BenchmarkRun,
    output_stream: TextIOWrapper,
    tmp_path: str,
) -> None:
    """
    Run a single benchmark with the given variant and output the results.

    :param benchmark: the benchmark to run
    :param variant: the variant to run the benchmark with
    :param output_stream: the stream to write the output to
    :param tmp_path: the temporary file path to write the output to during execution
    """
    times: list[float] = []
    memory_usages: list[float] = []
    for i in range(RUNS_PER_BENCHMARK + 1):
        cmd = TIME_CMD + [
            "python3",
            "-m",
            "octopus.main",
            "--output",
            tmp_path,
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
        if output_stream is None:
            print(result.stderr)
        else:
            output_stream.write(result.stderr + "\n")
            output_stream.flush()

        if i > 0:  # Skip the first run due to cold start effects
            time_match = re.search(
                r"Elapsed \(wall clock\) time.*?:\s*(?:(\d+):)?(\d+):(\d+(?:\.\d+)?)",
                result.stderr,
            )
            if time_match:
                hours = int(time_match.group(1)) if time_match.group(1) else 0
                minutes = int(time_match.group(2))
                seconds = float(time_match.group(3))
                total_time = hours * 3600 + minutes * 60 + seconds
                times.append(total_time)

            memory_match = re.search(
                r"Maximum resident set size \(kbytes\):\s*(\d+)",
                result.stderr,
            )
            if memory_match:
                memory_usage_kb = int(memory_match.group(1))
                mib = (memory_usage_kb * 1000) / (1024**2)
                memory_usages.append(mib)

    avg_time = statistics.mean(times)
    avg_memory_usage = statistics.mean(memory_usages)
    output = (
        f"({variant.name}) - benchmark {benchmark.name}: "
        f"avg. wall time: {avg_time:.2f} seconds, "
        f"avg. max. memory usage: {avg_memory_usage:.2f} MiB"
    )
    if output_stream is None:
        print(output)
    else:
        output_stream.write(output + "\n")
        output_stream.flush()


def main() -> None:
    """Entry point of the benchmark runner."""
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
