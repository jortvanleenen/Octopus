#!/usr/bin/env python3

import argparse
import subprocess
import sys
import re
import statistics
from itertools import combinations
from pathlib import Path


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

    wall_re = re.compile(r"Wall time:\s+([0-9.]+)\s+s")
    mem_re = re.compile(r"Peak memory:\s+([0-9.]+)\s+KiB")

    total = len(p4_files) * (len(p4_files) - 1) // 2
    completed = 0

    for file1, file2 in combinations(p4_files, 2):
        cmd = [
            "python3",
            "-m",
            "octopus.main",
            str(file1),
            str(file2),
            "--stat",
        ]

        print(f"Checking equivalence: {file1.name} <-> {file2.name}")

        try:
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
            )
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            break

        out = result.stdout
        print(result.stdout)
        print(result.stderr)

        wall_match = wall_re.search(out)
        mem_match = mem_re.search(out)

        if wall_match:
            wall_times.append(float(wall_match.group(1)))
        if mem_match:
            peak_mems.append(float(mem_match.group(1)))

        if wall_match or mem_match:
            completed += 1

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

    print("\n--- Peak memory (KiB) ---")
    for k, v in mem_stats.items():
        print(f"{k:>8}: {v:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run Octopus equivalence checks for all unordered pairs "
            "of P4 programs in a directory and report statistics."
        )
    )
    parser.add_argument(
        "directory",
        type=Path,
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
