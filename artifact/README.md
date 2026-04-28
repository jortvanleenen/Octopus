CAV 2026 Artifact
=======================================
Paper title: Octopus: Practical Equivalence Checking of P4 Packet Parsers

Claimed badges: Available + Reusable

Justification for the badges:

* Functional:
  The artifact is provided as a self-contained Docker image that replicates most
  of the experimental results presented in the paper. It includes the full
  Octopus implementation, all required dependencies (Python and system packages),
  benchmark P4 programs, and the relevant evaluation scripts.

  Replicated:
    - Comparison with Leapfrog (Table 1): point (1)
    - Synthetic benchmarks (Figure 3 + equivalence claims in Section 5, page 9): point (2)
    - Public code (statistics in Section 5, page 9): point (3)

  Not replicated:
    - Obtained performance results for Leapfrog in Table 1. We do not reproduce
      these results as part of the artifact evaluation. Re-running Leapfrog
      proved to be prohibitively time-consuming (runtime of multiple days) and
      requires substantial memory resources (~500 GB). Instead, we focus on
      reproducing the results for Octopus, which is the primary subject of this
      artifact. To ensure a fair comparison, we executed both tools on the same
      hardware platform. Our measurements for Leapfrog were generally higher
      (i.e., slower) than those reported in the original paper, but remained
      consistent with their overall findings and trends. Octopus remains faster
      than Leapfrog, also when considering their measurements. The Leapfrog
      implementation is publicly available at:
      https://github.com/verified-network-toolchain/leapfrog.

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
* Time (full review): 2 hours

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
requested to extend Octopus with certificate validation. This addition required
modest changes to the core algorithm and implementation, which in turn affect
performance characteristics such as runtime and memory usage. We also reduced
memory usage by redesigning the internal handling of formulas, eliminating the
need for expensive deep copies. Finally, we replaced the previously used cvc5
SMT solver with Z3. While both solvers exhibited comparable performance (within
approximately +/- 10%, as reported during the rebuttal phase), cvc5 triggered a
race condition in PySMT, our SMT interface, which motivated the switch.

As a result, the reported averages differ from those in the accepted paper,
although the underlying methodology remains unchanged. We have submitted the
original version of the accepted paper to the AE, as requested, but will use
the updated results in the camera-ready version.

We re-executed all experiments on the same hardware configuration as reported
in the paper to ensure comparability. The previously included cold-start phase
was removed, as it yielded only marginal improvements for very short runs while
substantially increasing overall runtime. The updated results are available
under `/our_results` and cover all three evaluation components:

- (1) updated Octopus averages for Table 1,
- (2) an updated version of Figure 3, and
- (3) updated summary statistics for the public code experiment.

For (1), we now report generation and validation times separately, whose sum is
comparable to the previously reported total execution time. For (2), we plot
the certificate generation time as well as the combined generation and
validation time.

Although specific measurements differ from those reported in the paper, the
overall trends and conclusions remain unchanged.

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

(1) To obtain the results in Table 1, run the following command: [~1.5 hours]

    python3 tests/runner.py --suite leapfrog

The experiment run averages will be printed out in the CLI. These should be
consistent with those in `our_results/1_Table_1_Octopus_averages.txt`.

(2) To obtain the results for the synthetic benchmarks experiment, run: [~20 minutes]

    python3 tests/runner.py --suite whippersnapper
    mv whippersnapper_plot.png /output/whippersnapper_plot.png

Once all experiments have ran, a plot will be generated and saved as
`whippersnapper_plot.png`. The second command moves the file to the `/output`
directory. This will also make it available on the host in
`octopus-results/` (or wherever you chose to bind the output directory). The
plot should align with ours in `our_results/2_Figure_3_Whippersnapper_plot.png`.

    python3 tests/runner.py --suite whippersnapper_equiv

The CLI output should confirm that the three pairs of parsers are indeed
equivalent, as claimed in the paper (Section 5, page 9, final paragraph of the
'Synthetic benchmarks' subsection).

(3) To obtain the results for the public code experiment, run the following command: [~5 minutes]

    python3 tests/public-code-exp.py --directory tests/p4-programs-survey

Once all comparisons have been performed, the final CLI output will consist of
statistical results, some of which are reported in the paper. These should be
consistent with those in `our_results/3_public_code__statistics.txt`.
