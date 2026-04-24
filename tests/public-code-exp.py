#!/usr/bin/env python3
"""
This module contains a runner for an experiment on public P4 code.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import argparse
import subprocess
import sys
import re
import statistics
from itertools import combinations
from pathlib import Path

from tqdm import tqdm

TIME_CMD = ["/usr/bin/time", "-v"]


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra

    def groups(self):
        result = {}
        for x in self.parent:
            root = self.find(x)
            result.setdefault(root, []).append(x)
        return result.values()


def find_p4_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.p4") if p.is_file())


def describe(values: list[float]) -> dict[str, float]:
    values = sorted(values)
    n = len(values)

    if n == 0:
        return {}

    def percentile(p: float) -> float:
        k = (n - 1) * p
        f = int(k)
        c = min(f + 1, n - 1)
        return values[f] + (values[c] - values[f]) * (k - f)

    return {
        "count": n,
        "min": values[0],
        "q1": percentile(0.25),
        "median": percentile(0.5),
        "q3": percentile(0.75),
        "max": values[-1],
        "mean": statistics.mean(values),
        "stdev": statistics.stdev(values) if n > 1 else 0.0,
    }


def run_equivalence_checks(p4_files: list[Path]) -> None:
    wall_times: list[float] = []
    peak_mems: list[float] = []

    uf = UnionFind()

    total = len(p4_files) * (len(p4_files) - 1) // 2
    completed = 0

    time_re = re.compile(
        r"Elapsed .*?:\s*(?:(\d+):)?(\d+):(\d+(?:\.\d+)?)"
    )
    mem_re = re.compile(
        r"Maximum resident set size .*?:\s*(\d+)"
    )

    with tqdm(total=total, desc="Equivalence checks") as pbar:
        for file1, file2 in combinations(p4_files, 2):
            cmd = TIME_CMD + [
                "python3",
                "-m",
                "octopus.main",
                str(file1),
                str(file2),
            ]

            try:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            except KeyboardInterrupt:
                print("\nInterrupted by user.")
                break

            out = result.stdout
            err = result.stderr

            t_match = time_re.search(err)
            if t_match:
                h = int(t_match.group(1)) if t_match.group(1) else 0
                total_sec = (
                        h * 3600
                        + int(t_match.group(2)) * 60
                        + float(t_match.group(3))
                )
                wall_times.append(total_sec)

            m_match = mem_re.search(err)
            if m_match:
                mem_mib = int(m_match.group(1)) / 1024
                peak_mems.append(mem_mib)

            output = out + err

            if "NOT equivalent" in output:
                verdict = "NOT equivalent"
            elif "equivalent" in output:
                verdict = "Equivalent"
            else:
                verdict = "Unknown"
                tqdm.write(f"Unknown: {file1.name} <-> {file2.name}")

            if verdict == "Equivalent":
                uf.union(file1.name, file2.name)

            if t_match or m_match:
                completed += 1

            pbar.update(1)

    print("\n=== Summary ===")
    print(f"Completed runs: {completed} / {total}")

    if completed == 0:
        print("No completed runs with statistics.")
        return

    wall_stats = describe(wall_times)
    mem_stats = describe(peak_mems)

    print("\n--- Wall time (seconds) ---")
    for k, v in wall_stats.items():
        print(f"{k:>8}: {v:.4f}")

    print("\n--- Peak memory (MiB) ---")
    for k, v in mem_stats.items():
        print(f"{k:>8}: {v:.2f}")

    print("\n=== Equivalent parser groups (size > 1) ===")

    groups = list(uf.groups())
    multi_groups = [g for g in groups if len(g) > 1]

    if not multi_groups:
        print("No equivalent parser groups found.")
    else:
        for i, group in enumerate(multi_groups, 1):
            print(f"Group {i}: {', '.join(sorted(group))}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run Octopus equivalence checks for all unordered pairs "
            "of P4 programs in a directory and report statistics."
        )
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path("p4-programs-survey"),
        help="Directory containing P4 programs",
    )

    args = parser.parse_args()
    directory: Path = args.directory

    if not directory.is_dir():
        print(f"Error: {directory} is not a directory.", file=sys.stderr)
        sys.exit(1)

    p4_files = find_p4_files(directory)

    if len(p4_files) < 2:
        print("Need at least two .p4 files to compare.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(p4_files)} P4 files")
    print(f"Total comparisons: {len(p4_files) * (len(p4_files) - 1) // 2}\n")

    run_equivalence_checks(p4_files)


if __name__ == "__main__":
    main()
