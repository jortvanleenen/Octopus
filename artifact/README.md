CAV 2026 Artifact
=======================================
Paper title: Octopus: Practical Equivalence Checking of P4 Packet Parsers

Claimed badges: Available + Reusable

Justification for the badges:

* Functional:
  The artifact is provided as a self-contained Docker image that replicates all
  the experimental results presented in the paper. It includes the full Octopus
  implementation, all required dependencies (Python and system packages),
  benchmark P4 programs, and the relevant evaluation scripts.

  Replicated:
    - Comparison with Leapfrog (Table 1): point (1)
    - Synthetic benchmarks (Figure 3 + equivalence claims, Section 5): point (2)
    - Public code (statistics, Section 5): point (3)

  Not replicated:
    - Obtained performance results for Leapfrog in Table 1. We do not reproduce
      these results as part of the artifact evaluation. Re-running Leapfrog proved
      to be prohibitively time-consuming (runtime of multiple days) and requires
      substantial memory resources (~500 GB). Instead, we focus on reproducing the
      results for Octopus, which is the primary subject of this artifact. To
      ensure a fair comparison, we executed both tools on the same hardware
      platform. Our measurements for Leapfrog were generally higher (i.e., slower)
      than those reported in the original paper, but remained consistent with
      their overall findings and trends. Octopus remains faster than Leapfrog,
      also when considering their measurements. The Leapfrog implementation is
      publicly available at: https://github.com/verified-network-toolchain/leapfrog.

* Reusable:
  The Octopus tool is open-source and available via a public GitHub repository
  (https://github.com/jortvanleenen/Octopus) under the permissive MIT license.
  The repository supports manual installation and includes full documentation
  and usage instructions. The codebase is modular, structured, and documented to
  support reuse and extension. The repository also includes example inputs, as
  well as both correct and incorrect test cases to facilitate validation and
  experimentation. It also provides the benchmark infrastructure for systematic
  evaluation.

  In addition to the Docker image, a complete version of this repository is
  included in the artifact archive (`Repository.zip`). Using the repository
  (see its `README.md` for more elaborate instructions) does require external
  connectivity (e.g., to fetch dependencies), but it is not required for
  reproducing the results reported in the paper, which can be done using the
  provided Docker image (which is based on the same Octopus source code).

Differences to the paper's results due to required post-rebuttal changes are 
documented in the FULL REVIEW section.

Requirements:

* RAM: 16 GiB
* CPU cores: 4
* Time (smoke test): 15 minutes
* Time (full review): 4 hours

external connectivity: NO

-------------------------------------------------------------------------------
**                                SMOKE TEST                                 **
-------------------------------------------------------------------------------

Run the following command to load the Docker image:

    docker load < octopus.tar.gz

Then, execute a derived container with:

    docker run --rm jortvanleenen/octopus:latest tests/correct_cases/hello-octopus.p4 tests/correct_cases/hello-octopus.p4

This command starts a container from the image and runs Octopus on a single,
test P4 program. The optional `--rm` flag ensures the container is removed after
execution.

The input program is checked for bisimilarity (a self-check in this case). A
successful run produces output of the form:

    The two parsers are equivalent.
    --- Bisimulation Certificate ---
    GuardedFormula(...)
    GuardedFormula(...)

where "..." denotes the full content of each guarded formula.

Successful execution confirms that both the P4 parsing pipeline and SMT-based
reasoning are functioning correctly. You can then proceed to the full
experimental evaluation.

-------------------------------------------------------------------------------
**                               FULL REVIEW                                 **
-------------------------------------------------------------------------------

It should be noted that, following the rebuttal phase, we were explicitly
requested to extend Octopus with certificate validation. This addition
required modest changes to the core algorithm and its implementation, which
in turn affect performance characteristics such as runtime and memory usage.
As a result, the reported averages for these metrics may differ from those
presented in the original paper, even though the underlying methodology
remains the same.

To ensure a fair comparison, we re-executed all experiments on the same
hardware configuration as used in the paper. The updated results are
included under `/our_output` and cover all three evaluation components:
(1) updated Octopus averages for Table 1, (2) an updated version of Figure 3, 
and (3) updated summary statistics for the public code experiment.

While measurements differ from those reported in the paper, the overall
trends and conclusions remain unchanged.

Assuming the smoke test passed, run the following commands to reproduce the
results.

First, create a directory on your host to store results:

    mkdir octopus-results

Then, start an interactive container (that will be removed when exiting the
session (optional `--rm` again)) with a bind mount to the created directory to
persist results:

    docker run -it --rm -v $(pwd)/octopus-results:/output --entrypoint /bin/bash jortvanleenen/octopus:latest

> **Note**
>
> The local results directory is represented as `$(pwd)/octopus-results`.
>
> If you are using a different shell, adjust the syntax for resolving the current
> working directory accordingly. Likewise, update the path if you chose a
> different directory for storing results.

You are now in a bash environment within the container, where you can run the
experiments and inspect the source code. Source code is located in the `/src`
directory. The experiments can be found in the `/tests` directory. Any files
written to `/output` will be available on the host in the `octopus-results`
directory (or wherever you chose to bind the output directory).

The following commands will print out progress as they execute the benchmarks.
While concrete output values may differ, the overall trends (e.g., ratios)
should stay the same.

(1) To obtain the results in Table 1, run the following command:

    python3 tests/runner.py --suite leapfrog

    The experiment run averages will be printed out in the CLI.

(2) To obtain the results for the synthetic benchmarks experiment, run:

    python3 tests/runner.py --suite whippersnapper
    mv whippersnapper_plot.png /output/whippersnapper_plot.png

    Once all experiments have ran, a plot will be generated and saved as 
    `whippersnapper_plot.png`. The second command moves the file to the `/output` 
    directory. This will also make it available on the host in 
    `octopus-results/` (or wherever you chose to bind the output directory).

    python3 tests/runner.py --suite whippersnapper_equiv --variant octopus_default

    The CLI output should confirm that the three pairs of parsers are indeed 
    equivalent, as claimed in the paper.

(3) To obtain the results for the public code experiment, run the following command:

    python3 tests/public-code-exp.py --directory tests/p4-programs-survey

    Once all comparisons have been performed, the final CLI output will consist 
    of a summary of statistical results, some of which are reported in the paper.
