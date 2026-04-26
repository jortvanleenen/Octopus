# Octopus

Octopus is an equivalence checker for P4 packet parsers, implemented in Python.  
Its implementation uses symbolic bisimulation to compare parser behavior.

Octopus is accompanied by the paper *"Octopus: Practical Equivalence Checking of
P4 Packet Parsers"* by Jort van Leenen and Dr. Tobias Kappé. This work builds on
the first author's bachelor's thesis "[*Practical Equivalence Checking of P4
Packet Parsers*](https://theses.liacs.nl/3410)", supervised by Dr. Tobias Kappé and Jan Martens. The
implementation builds on theoretical work from [Leapfrog](https://doi.org/10.48550/arXiv.2205.08762), a Rocq-based
formal verifier for P4 packet parsers.

## Features

- Equivalence checking for P4 packet parsers using (optimized) symbolic
  bisimulation;
- Support for IR (JSON) format from `p4c-graphs`;
- CLI interface with structured output.

## Limitations

- Only a subset of P4_16 constructs and features are supported.

## Dependencies and Compatibility

Octopus depends on the `p4c-graphs` tool to generate the IR JSON representation
of P4 programs.

- Tested with: `p4c-graphs` version 1.2.x.x;
- Requires: Python 3.12 or later; tested up to 3.13.

Ensure `p4c-graphs` is available on your system's `PATH` if you provide P4
programs as input.

## Docker

Octopus is [available as a prebuilt Docker image](https://hub.docker.com/repository/docker/jortvanleenen/octopus),
hosted on Docker Hub.

To download the image:

```bash
docker pull jortvanleenen/octopus:latest
```

You can verify the installation by performing a self-check on a simple P4
program:

```bash
docker run --rm jortvanleenen/octopus:latest tests/correct_cases/hello-octopus.p4 tests/correct_cases/hello-octopus.p4
```

The `--rm` flag ensures the container is removed after execution. Successful
execution confirms that both the P4 parsing pipeline and SMT-based reasoning are
functioning correctly.

To check your own P4 programs, mount a local directory (e.g., the current
working directory) into the container. The example below mounts the current
working directory to `/workspace` and sets that as the working directory:

```bash
docker run --rm -v "$PWD:/workspace" -w /workspace jortvanleenen/octopus:latest [OPTIONS] FILE1 FILE2
```

> **Note**
>
> The above command represents the current working directory as `$PWD`.
> If you're using a different operating system or shell, you may need to adjust
> this variable accordingly.

The image comes with the Z3 and cvc5 SMT solvers preinstalled. To install
additional solvers or configure custom PySMT setups, use an interactive shell:

```bash
docker run -it --rm --entrypoint /bin/bash jortvanleenen/octopus:latest
```

You can then, for example, use `pysmt-install` to install SMT solvers. For more
information, see the manual installation instructions below.

## Manual Installation

To install Octopus, the following steps can be followed. Step 6 installs the
project in editable mode, including development dependencies. Feel free to
customise this step according to your needs. For example, one could decide to
install only the runtime dependencies by removing `[dev]`.

```bash
# 1. Clone the repository
git clone https://github.com/jortvanleenen/Octopus.git
cd Octopus

# 2. Create a virtual environment
python3 -m venv .venv

# 3. Activate the virtual environment
source .venv/bin/activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install Hatch (build + env management tool)
pip install hatch

# 6. Install the project with dev dependencies
pip install -e .[dev]
```

Following the above instructions should make the `octopus` command available in
your environment.

To use symbolic bisimulation, at least one SMT solver has to be installed
locally. PySMT, a dependency of Octopus and thus installed in step 6, provides
the `pysmt-install` command to make doing this simple. For example, to install
Z3 and cvc5, run: `pysmt-install --cvc5 --z3`. Afterwards,
`pysmt-install --check` can be used to verify the installation.

## Usage

```
octopus [OPTIONS] FILE1 FILE2
```

`FILE1` and `FILE2` are paths to the two P4 programs to compare. These can be
either `.p4` source files, or IR JSON files produced by `p4c-graphs`. One has to
provide the `-j` option to Octopus in the latter case.

### CLI Options

Octopus provides a command-line interface (CLI) with the following options:

| Short | Long                          | Description                                                                |
|-------|-------------------------------|----------------------------------------------------------------------------|
| `-h`  | `--help`                      | Show a help message and exit                                               |
|       | `--version`                   | Show the version of Octopus and exit                                       |
| `-j`  | `--json`                      | Specify that both inputs are in IR (p4c) JSON format                       |
|       | `file1`                       | Path to the first P4 program                                               |
|       | `file2`                       | Path to the second P4 program                                              |
| `-v`  | `--verbosity`                 | Increase output verbosity (`-v`, `-vv`, `-vvv`)                            |
| `-L`  | `--disable_leaps`             | Disable leaps; only use single-step bisimulation                           |
| `-o`  | `--output`                    | Write the bisimulation certificate or counterexample to the specified file |
|       | `--no-conclusion`             | Do not print the final conclusion (equivalent or not) in the CLI output    |
|       | `--no-validation`             | Do not validate that the generated certificate represents a bisimulation   |
| `-f`  | `--fail-on-mismatch`          | Exit with code 1 if the parsers are not equivalent                         |
| `-s`  | `--solvers`                   | Specify which SMT solvers to use along with their options                  |
|       | `--solvers-global-options`    | Specify global options for all solvers                                     |
|       | `--filter-accepting-string`   | Define an additional constraint for accepting pairs via a string           |
|       | `--filter-accepting-file `    | Define an additional constraint for accepting pairs via an external file   |
|       | `--filter-disagreeing-string` | Define an additional constraint for disagreeing pairs via a string         |
|       | `--filter-disagreeing-file`   | Define an additional constraint for disagreeing pairs via an external file |

### Examples

Check two IR JSON files (using symbolic bisimulation):

```shell
octopus -j parser1.json parser2.json
```

Check two P4 source files (Octopus invokes `p4c-graphs` internally):

```shell
octopus program1.p4 program2.p4
```

Write output (certificate or counterexample) to a file:

```shell
octopus program1.p4 program2.p4 --output result.txt
```

Exit with status code 1 if the parsers are not equivalent and show no output:

```shell
octopus program1.p4 program2.p4 --fail-on-mismatch --no-conclusion
```

> **Note**
>
> The above options are useful for scripting and CI/CD pipelines.

Customize the SMT solver portfolio and provide (global) options:

```shell
octopus -j program1.p4 program2.p4 \
--solvers '["z3",("cvc5",{"incremental":False})]' \
--solvers-global-options '{"generate_models":False}'
```

> **Note**
>
> Evaluation of the options is done using `ast.literal_eval()`, so the argument
> must be a valid Python literal.
>
> For `--solvers`, the following object is accepted: `list[str | tuple[str, dict[str, Any]]]`.
>
> For `--solvers-global-options`, the following object is accepted: `dict[str, Any]`.

Perform external filtering by specifying an additional constraint that must hold
for accepting pairs:

```shell
octopus p1.p4 p2.p4 \
"hdr_l.hdr.field0 == (hdr_r.hdr.field1 + hdr_r.hdr.field2) and hdr_l.hdr.field0[15:0] == '0xABCD_16' and True or False"
```

> **Note**
>
> A (larger) constraint can also be specified using an external file with the
`--filter-accepting-file` option. Evaluation of these options is done using
> `ast.parse()` (mode eval), so the argument must be a valid Python expression.
> Similarly to above, a constraint can be provided that should hold for
> disagreeing pairs using `--filter-disagreeing-string` and
> `--filter-disagreeing-file` respectively.

## Verifying Claims and Benchmarking

To verify the claims made in the paper, you can run the benchmark scripts, which
are also included in the Docker image. A brief overview follows below. More
detailed information and steps can be found in the `artifact/README.md` file.

- `tests/runner.py` automates the running of benchmarks, including the
  aggregation of results and generation of statistics. It is used for our claims
  regarding Leapfrog and Whippersnapper.
- `tests/public-code-exp.py` is responsible for the experiments on public code,
  including the generation of statistics and equivalence classes over the
  `tests/p4-programs-survey` parsers.

### Leapfrog Benchmarks

The Leapfrog benchmark set is taken from Doenges et al. (2022). As our manner of
input differs from theirs, we have provided a mapping from our folder names to
their benchmark filenames.

- **States** denotes the total number of states in both parser programs.
- **Branched** is the number of bits tested in all `transition select` statements.
- **Total** is the total number of bits across all variables.

| Category      | Name                     | File                  | States | Branched (b) | Total (b) |
|---------------|--------------------------|-----------------------|--------|--------------|-----------|
| Utility       | State rearrangement      | `IPFilter`            | 5      | 8            | 256       |
|               | Variable-length format 2 | `IPOptions2`          | 30     | 32           | 672       |
|               | Variable-length format 3 | `IPOptions3`          | 45     | 96           | 672       |
|               | Header initialisation    | `SelfComparison`      | 10     | 12           | 736       |
|               | Speculative extraction   | `MPLSVectorized`      | 5      | 3            | 192       |
|               | Relational verification  | `SloppyStrictStores`  | 6      | 32           | 1056      |
|               | External filtering       | `SloppyStrictFilter`  | 6      | 32           | 1056      |
| Applicability | Edge                     | `EdgeSelf`            | 28     | 52           | 2584      |
|               | Service provider         | `ServiceproviderSelf` | 22     | 25           | 2536      |
|               | Datacenter               | `DataCenterSelf`      | 30     | 274          | 2272      |
|               | Enterprise               | `EnterpriseSelf`      | 22     | 80           | 1952      |
|               | Translation validation   | `EdgeTrans`           | 30     | 56           | 3036      |

> **Notes**
>
> - Full filenames in Leapfrog are `<name-in-table>Proof.v`, except for
    > `SloppyStrictStores` and `SloppyStrictFilter`, which are as is.
> - The Leapfrog GitHub repository incorrectly lists `EthernetProof.v` as the
    > benchmark file for *state rearrangement*.
> - The number of branched and total bits have been corrected for most
    > benchmarks, as these were incorrect in the Leapfrog paper.
> - In Leapfrog's Enterprise benchmark, the size of the IPv4 header was
    > incorrectly specified. We were able to adjust this to the correct value by
    > looking at the original code in
    the [parser-gen repository](https://github.com/grg/parser-gen/blob/master/examples/headers-enterprise.txt).

## License

This project is licensed under the MIT License. See the `LICENSE` file for
details.