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
    - Synthetic benchmarks (Figure 3): point (2)
    - Public code application (as described in the text, Section 5): point (3)

* Reusable:
  The Octopus tool is open-source and available via a public GitHub repository
  under the permissive MIT license. The repository supports manual installation
  and includes full documentation and usage instructions. The codebase is modular,
  structured, and documented to support reuse and extension. The repository also
  includes example inputs, as well as both correct and incorrect test cases to
  facilitate validation and experimentation. It also provides the benchmark
  infrastructure for systematic evaluation.

  In addition to the Docker image, a complete version of this repository is
  included in the artifact archive. Using the repository does require external
  connectivity (e.g., to fetch dependencies), but it is not required for
  reproducing the results reported in the paper, which can be done using the
  provided Docker image (which is based on the same Octopus source code).

Requirements:

* RAM: 16 GiB
* CPU cores: 4
* Time (smoke test): 30 minutes
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

where "..." denotes the full guarded formula output.

Successful execution confirms that both the P4 parsing pipeline and SMT-based
reasoning are functioning correctly. You can then proceed to the full
experimental evaluation.

-------------------------------------------------------------------------------
**                               FULL REVIEW                                 **
-------------------------------------------------------------------------------

Assuming the smoke test passed, run the following commands to reproduce the
results. Running the full benchmark suite can take around 4 hours on a standard,
modern laptop.

First, create a directory on your host to store results:

    mkdir octopus-results

Then, start an interactive container (that will be removed when exiting the
session (optional `--rm` again)) with a bind mount to persist results:

    docker run -it --rm -v $(pwd)/octopus-results:/output --entrypoint /bin/bash jortvanleenen/octopus:latest

You are now in a bash environment within the container, where you can run the
experiments and inspect the source code. Source code is located in the `/src`
directory. The experiments can be found in the `/tests` directory. Any files
written to `/output` will be available on the host in the `octopus-results`
directory.

The following commands will print out progress as they execute the benchmarks.
While concrete output values may differ, the overall trends (e.g., ratios)
should stay the same.

(1) To obtain the results in Table 1, run the following command:

    python3 tests/runner.py --suite leapfrog

    The experiment run averages will be printed out in the CLI.

(2) To generate Figure 3, run the following command:

    cd /output
    python3 tests/runner.py --suite whippersnapper
    cd ..
    
    Once all experiments have ran, a plot will be generated and saved as 
    `whippersnapper_plot.png` in the `/output` directory. This file will also 
    be available on the host in `octopus-results/whippersnapper_plot.png`. The 
    plot should look similar to the one in the paper, with roughly the same 
    ratios.

(3) To obtain the results for the public code experiment, run the following command:

    python3 tests/public-code-exp.py --directory tests/p4-programs-survey

    Once all comparisons have been performed, the final CLI output will consist 
    of a summary of the statistical results, which are reported in the paper.
