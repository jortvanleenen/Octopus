# Kangaroo

Kangaroo is an equivalence checker for P4 packet parsers, implemented in Python.  
It supports both naive and optimised symbolic bisimulation techniques for comparing parser behaviour.

Kangaroo is accompanied by the paper *"Practical Equivalence Checking of P4 Parsers"* by Jort van Leenen.  
The implementation builds on earlier work from [Leapfrog](https://doi.org/10.48550/arXiv.2205.08762), a Rocq-based
formal verifier for P4 parsers.

## Features

- Equivalence checking for P4 parsers using either naive or (optimised) symbolic bisimulation;
- Support for IR (JSON) format from `p4c-graphs`;
- CLI interface with structured output;
- Lightweight and dependency-free (except for SMT solving).

## Limitations

- Only supports P4-16 parsers;
- Only supports a subset of P4-16 constructs and features;

## Dependencies and Compatibility

Kangaroo depends on the `p4c-graphs` tool to generate the IR JSON representation of P4 programs.

- Tested with: `p4c-graphs` version 1.2.4.2
- Requires: Python 3.10 or later (tested up to 3.13)

Ensure `p4c-graphs` is available on your system's `PATH`.

## Installation

To install Kangaroo, the following steps can be followed.
Step 6 installs the project in development mode, including development dependencies.
Feel free to customise this step according to your needs.
For example, one could decide to install only the runtime dependencies by skipping `[dev]`.

```bash
# 1. Clone the repository
git clone https://github.com/jortvanleenen/Kangaroo.git
cd Kangaroo

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

This makes the `kangaroo` command available in your environment.

To use symbolic bisimulation, at least one SMT solver has to be installed locally.
PySMT provides the `pysmt-install` command to make doing this simple.

For example, to install Z3 and cvc5, run: `pysmt-install --cvc5 --z3`.
Afterwards, `pysmt-install --check` can be used to verify the installation.

## Usage

```
kangaroo [OPTIONS] FILE1 FILE2
```

`FILE1` and `FILE2` are paths to the two P4 programs to compare. These can be either `.p4` source files or IR JSON files
produced by `p4c-graphs` (with the `-j` option).

### Examples

Check two IR JSON files:

```
kangaroo -j parser1.json parser2.json
```

Check two P4 source files (Kangaroo invokes `p4c-graphs` internally):

```
kangaroo program1.p4 program2.p4
```

Use symbolic bisimulation with leaps disabled:

```
kangaroo program1.p4 program2.p4 --disable_leaps
```

Write output (certificate or counterexample) to a file:

```
kangaroo -j parser1.json parser2.json --output result.txt
```

Exit with status code 1 if the parsers are not equivalent:

```
kangaroo -j parser1.json parser2.json --fail-on-mismatch
```

_Note: this is useful for scripting or CI/CD pipelines._

Print execution time (wall and CPU time):

```
kangaroo -j parser1.json parser2.json --time
```

## CLI Options

Kangaroo provides a command-line interface (CLI) with the following options:

| Short | Long                 | Description                                                                |
|-------|----------------------|----------------------------------------------------------------------------|
| `-h`  | `--help`             | Show a help message and exit                                               |
|       | `--version`          | Show the version of Kangaroo and exit                                      |
| `-j`  | `--json`             | Specify that both inputs are in IR (p4c) JSON format                       |
|       | `file1`              | Path to the first P4 program                                               |
|       | `file2`              | Path to the second P4 program                                              |
| `-v`  | `--verbosity`        | Increase output verbosity (`-v`, `-vv`, `-vvv`)                            |
| `-n`  | `--naive`            | Use naive bisimulation instead of symbolic bisimulation                    |
|       | `--disable_leaps`    | Disable leaps in symbolic bisimulation (ignored if `--naive` is set)       |
| `-o`  | `--output`           | Write the bisimulation certificate or counterexample to the specified file |
|       | `--fail-on-mismatch` | Exit with code 1 if the parsers are not equivalent                         |
| `-t`  | `--time`             | Measure and print bisimulation execution time                              |

## License

This project is licensed under the MIT License.
See the `LICENSE` file for details.