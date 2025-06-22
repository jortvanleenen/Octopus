# Octopus

Octopus is an equivalence checker for P4 packet parsers, implemented in Python.  
It supports both naive and optimised symbolic bisimulation techniques for comparing parser behaviour.

Octopus is accompanied by the paper *"Practical Equivalence Checking of P4 Packet Parsers"* by Jort van Leenen.  
The implementation builds on earlier work from [Leapfrog](https://doi.org/10.48550/arXiv.2205.08762), a Rocq-based
formal verifier for P4 parsers.

## Features

- Equivalence checking for P4 parsers using either naive or (optimised) symbolic bisimulation;
- Support for IR (JSON) format from `p4c-graphs`;
- CLI interface with structured output;
- Lightweight and dependency-free, excluding SMT solvers required for symbolic bisimulation.

## Limitations

- Only supports P4-16 parsers;
- Only supports a subset of P4-16 constructs and features.

## Dependencies and Compatibility

Octopus depends on the `p4c-graphs` tool to generate the IR JSON representation of P4 programs.

- Tested with: `p4c-graphs` version 1.2.4.2
- Requires: Python 3.10 or later (tested up to 3.13)

Ensure `p4c-graphs` is available on your system's `PATH`.

## Docker

Octopus is available as a prebuilt Docker image, [hosted on Docker Hub](https://hub.docker.
com/repository/docker/jortvanleenen/octopus).

To download the image:

```bash
docker pull jortvanleenen/octopus:latest
```

You can verify the installation by performing a self-check on a simple P4 program:

```bash
docker run --rm jortvanleenen/octopus:latest \
  tests/correct_cases/hello-octopus.p4 tests/correct_cases/hello-octopus.p4
```

This should confirm that Octopus is functioning correctly.

To check your own P4 programs, mount a local directory (e.g., the current working directory) into the container.
The example below mounts the current working directory to `/workspace` and sets that as the working directory:

```bash
docker run --rm -v "$PWD:/workspace" -w /workspace jortvanleenen/octopus:latest \
  [OPTIONS] FILE1 FILE2
```

The image includes the Z3 and cvc5 SMT solvers preinstalled.
To install additional solvers, or to run custom PySMT configurations, use an interactive shell:

```bash
docker run -it --rm jortvanleenen/octopus:latest /bin/bash
```

You can then, for example, use `pysmt-install` to install SMT solvers.
For more information, see the manual installation instructions below.

## Manual Installation

To install Octopus, the following steps can be followed.
Step 6 installs the project in editable mode, including development dependencies.
Feel free to customise this step according to your needs.
For example, one could decide to install only the runtime dependencies by removing `[dev]`.

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

This makes the `octopus` command available in your environment.

To use symbolic bisimulation, at least one SMT solver has to be installed locally.
PySMT provides the `pysmt-install` command to make doing this simple.

For example, to install Z3 and cvc5, run: `pysmt-install --cvc5 --z3`.
Afterwards, `pysmt-install --check` can be used to verify the installation.

## Usage

```
octopus [OPTIONS] FILE1 FILE2
```

`FILE1` and `FILE2` are paths to the two P4 programs to compare.
hese can be either `.p4` source files, or IR JSON files produced by `p4c-graphs` (with the `-j` option).

### Examples

Check two IR JSON files (using symbolic bisimulation by default):

```
octopus -j parser1.json parser2.json
```

Check two P4 source files (Octopus invokes `p4c-graphs` internally):

```
octopus program1.p4 program2.p4
```

Use symbolic bisimulation with leaps disabled:

```
octopus program1.p4 program2.p4 --disable_leaps
```

Write output (certificate or counterexample) to a file:

```
octopus -j parser1.json parser2.json --output result.txt
```

Exit with status code 1 if the parsers are not equivalent:

```
octopus -j parser1.json parser2.json --fail-on-mismatch
```

_Note: this is useful for scripting or CI/CD pipelines._

Print bisimulation execution time and memory usage:

```
octopus -j parser1.json parser2.json --stat
```

Customise the SMT solver portfolio and provide (global) options:

```
octopus -j p1.json p2.json \
--solvers ["z3", ("cvc5", {"incremental": False})] \
--solvers-global-options {"generate_models": False}
```

_Note: evaluation of the options is done using `ast.literal_eval()`, so it must be a valid Python literal._
_For `--solvers`, the following object is accepted: `list[str | tuple[str, dict[str, Any]]]`._
_For `--solvers-global-options`, the following object is accepted: `dict[str, Any]`._

## CLI Options

Octopus provides a command-line interface (CLI) with the following options:

| Short | Long                       | Description                                                                |
|-------|----------------------------|----------------------------------------------------------------------------|
| `-h`  | `--help`                   | Show a help message and exit                                               |
|       | `--version`                | Show the version of Octopus and exit                                       |
| `-j`  | `--json`                   | Specify that both inputs are in IR (p4c) JSON format                       |
|       | `file1`                    | Path to the first P4 program                                               |
|       | `file2`                    | Path to the second P4 program                                              |
| `-v`  | `--verbosity`              | Increase output verbosity (`-v`, `-vv`, `-vvv`)                            |
| `-n`  | `--naive`                  | Use naive bisimulation instead of symbolic bisimulation                    |
|       | `--disable_leaps`          | Disable leaps in symbolic bisimulation (ignored if `--naive` is set)       |
| `-o`  | `--output`                 | Write the bisimulation certificate or counterexample to the specified file |
|       | `--fail-on-mismatch`       | Exit with code 1 if the parsers are not equivalent                         |
|       | `--stat`                   | Measure and print bisimulation execution time and memory usage             |
| `-s`  | `--solvers`                | Specify which SMT solvers to use along with their options                  |
|       | `--solvers-global-options` | Specify global options for all solvers                                     |

## License

This project is licensed under the MIT License.
See the `LICENSE` file for details.