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
    arguments: dict[str, Any] = None


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
        # Benchmark(
        #     "datacenter",
        #     Path("tests/leapfrog_benchmarks/datacenter/switch.p4"),
        #     Path("tests/leapfrog_benchmarks/datacenter/switch.p4"),
        # ),
        # Benchmark(
        #     "edge_self",
        #     Path("tests/leapfrog_benchmarks/edge/plain.p4"),
        #     Path("tests/leapfrog_benchmarks/edge/plain.p4"),
        # ),
        # Benchmark(
        #     "edge_optimised",
        #     Path("tests/leapfrog_benchmarks/edge/plain.p4"),
        #     Path("tests/leapfrog_benchmarks/edge/optimised.p4"),
        # ),
        # Benchmark(
        #     "enterprise",
        #     Path("tests/leapfrog_benchmarks/enterprise/router.p4"),
        #     Path("tests/leapfrog_benchmarks/enterprise/router.p4"),
        # ),
        # Benchmark(
        #     "external_filtering",
        #     Path("tests/leapfrog_benchmarks/external_filtering/sloppy.p4"),
        #     Path("tests/leapfrog_benchmarks/external_filtering/strict.p4"),
        #     arguments={
        #         "filter-disagreeing-string":
        #             "hdr_r.eth.data[15:0] != '0x8600_16' and hdr_r.eth.data[15:0] != '0x86dd_16'"},
        # ),
        # Benchmark(
        #     "relational_verification",
        #     Path("tests/leapfrog_benchmarks/external_filtering/sloppy.p4"),
        #     Path("tests/leapfrog_benchmarks/external_filtering/strict.p4"),
        #     arguments={
        #         "filter-accepting-string":
        #             "((hdr_l.eth.data[15:0] == '0x8600_16' and hdr_l.ipv4.data == hdr_r.ipv4.data) "
        #             "or (hdr_l.eth.data[15:0] == '0x86dd_16' and hdr_l.ipv6.data == hdr_r.ipv6.data))",
        #         "filter-disagreeing-string": "True",
        #     },
        # ),
        # Benchmark(
        #     "header_initialisation",
        #     Path("tests/leapfrog_benchmarks/header_initialisation/correct.p4"),
        #     Path("tests/leapfrog_benchmarks/header_initialisation/correct.p4"),
        # ),
        # Benchmark(
        #     "service_provider",
        #     Path("tests/leapfrog_benchmarks/service_provider/core_router.p4"),
        #     Path("tests/leapfrog_benchmarks/service_provider/core_router.p4"),
        # ),
        # Benchmark(
        #     "speculative_extraction",
        #     Path("tests/leapfrog_benchmarks/speculative_extraction/mpls.p4"),
        #     Path("tests/leapfrog_benchmarks/speculative_extraction/mpls_vectorised.p4"),
        # ),
        # Benchmark(
        #     "state_rearrangement",
        #     Path("tests/leapfrog_benchmarks/state_rearrangement/combined_states.p4"),
        #     Path("tests/leapfrog_benchmarks/state_rearrangement/separate_states.p4"),
        # ),
        # Benchmark(
        #     "variable_length_formats_2",
        #     Path("tests/leapfrog_benchmarks/variable_length_formats_2/ipoptions.p4"),
        #     Path("tests/leapfrog_benchmarks/variable_length_formats_2/timestamp.p4"),
        # ),
        # Benchmark(
        #     "variable_length_formats_3",
        #     Path("tests/leapfrog_benchmarks/variable_length_formats_3/ipoptions.p4"),
        #     Path("tests/leapfrog_benchmarks/variable_length_formats_3/timestamp.p4"),
        # ),
        Benchmark(
            "parse_field_1",
            Path("tests/whippersnapper/parse-field/1.p4"),
            Path("tests/whippersnapper/parse-field/1.p4"),
        ),
        # Benchmark(
        #     "parse_field_4",
        #     Path("tests/whippersnapper/parse-field/4.p4"),
        #     Path("tests/whippersnapper/parse-field/4.p4"),
        # ),
        # Benchmark(
        #     "parse_field_16",
        #     Path("tests/whippersnapper/parse-field/16.p4"),
        #     Path("tests/whippersnapper/parse-field/16.p4"),
        # ),
        # Benchmark(
        #     "parse_field_64",
        #     Path("tests/whippersnapper/parse-field/64.p4"),
        #     Path("tests/whippersnapper/parse-field/64.p4"),
        # ),
        # Benchmark(
        #     "parse_header_4_1",
        #     Path("tests/whippersnapper/parse-header/4-1.p4"),
        #     Path("tests/whippersnapper/parse-header/4-1.p4"),
        # ),
        # Benchmark(
        #     "parse_header_4_4",
        #     Path("tests/whippersnapper/parse-header/4-4.p4"),
        #     Path("tests/whippersnapper/parse-header/4-4.p4"),
        # ),
        # Benchmark(
        #     "parse_header_4_16",
        #     Path("tests/whippersnapper/parse-header/4-16.p4"),
        #     Path("tests/whippersnapper/parse-header/4-16.p4"),
        # ),
        Benchmark(
            "parse_header_4_32",
            Path("tests/whippersnapper/parse-header/4-32.p4"),
            Path("tests/whippersnapper/parse-header/4-32.p4"),
        ),
        # Benchmark(
        #     "parse_header_1_64",
        #     Path("tests/whippersnapper/parse-header/1-64.p4"),
        #     Path("tests/whippersnapper/parse-header/1-64.p4"),
        # ),
        # Benchmark(
        #     "parse_header_1_98",
        #     Path("tests/whippersnapper/parse-header/1-98.p4"),
        #     Path("tests/whippersnapper/parse-header/1-98.p4"),
        # ),
        # Benchmark(
        #     "parse_complex_2_2",
        #     Path("tests/whippersnapper/parse-complex/2-2.p4"),
        #     Path("tests/whippersnapper/parse-complex/2-2.p4"),
        # ),
        # Benchmark(
        #     "parse_complex_2_4",
        #     Path("tests/whippersnapper/parse-complex/2-4.p4"),
        #     Path("tests/whippersnapper/parse-complex/2-4.p4"),
        # ),
        # Benchmark(
        #     "parse_complex_2_6",
        #     Path("tests/whippersnapper/parse-complex/2-6.p4"),
        #     Path("tests/whippersnapper/parse-complex/2-6.p4"),
        # ),
        # Benchmark(
        #     "parse_complex_3_3",
        #     Path("tests/whippersnapper/parse-complex/3-3.p4"),
        #     Path("tests/whippersnapper/parse-complex/3-3.p4"),
        # ),
        # Benchmark(
        #     "parse_complex_3_4",
        #     Path("tests/whippersnapper/parse-complex/3-4.p4"),
        #     Path("tests/whippersnapper/parse-complex/3-4.p4"),
        # ),
        # Benchmark(
        #     "parse_complex_4_2",
        #     Path("tests/whippersnapper/parse-complex/4-2.p4"),
        #     Path("tests/whippersnapper/parse-complex/4-2.p4"),
        # ),
        # Benchmark(
        #     "parse_complex_4_3",
        #     Path("tests/whippersnapper/parse-complex/4-3.p4"),
        #     Path("tests/whippersnapper/parse-complex/4-3.p4"),
        # ),
        # Benchmark(
        #     "parse_complex_6_2",
        #     Path("tests/whippersnapper/parse-complex/6-2.p4"),
        #     Path("tests/whippersnapper/parse-complex/6-2.p4"),
        # ),
        # Benchmark(
        #     "equiv_field_4_and_header_4_1",
        #     Path("tests/whippersnapper/parse-field/4.p4"),
        #     Path("tests/whippersnapper/parse-header/4-1.p4"),
        # ),
        # Benchmark(
        #     "subset_field_4_and_header_4_4",
        #     Path("tests/whippersnapper/parse-field/4.p4"),
        #     Path("tests/whippersnapper/parse-header/4-4.p4"),
        #     arguments={
        #         "filter-disagreeing-string":
        #             "hdr_r.header_0.field_0 != '0_16'",
        #     }
        # ),
        # Benchmark(
        #     "subset_field_1_and_complex_3_1",
        #     Path("tests/whippersnapper/parse-field/1.p4"),
        #     Path("tests/whippersnapper/parse-complex/3-1.p4"),
        #     arguments={
        #         "filter-disagreeing-string":
        #             "hdr_r.ptp.reserved2 == '1_8'",
        #     }
        # ),
        Benchmark(
            "parse_complex_4_4",
            Path("tests/whippersnapper/parse-complex/4-4.p4"),
            Path("tests/whippersnapper/parse-complex/4-4.p4"),
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

        if variant.arguments:
            for arg_name, arg_value in variant.arguments.items():
                cmd.extend([f"--{arg_name}", str(arg_value)])

        if benchmark.arguments:
            for arg_name, arg_value in benchmark.arguments.items():
                cmd.extend([f"--{arg_name}", str(arg_value)])

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
                mib = (memory_usage_kb * 1000) / (1024 ** 2)
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
