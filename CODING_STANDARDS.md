# Coding Standards

Our contribution workflow requires you to format and lint your code before committing it.
This can be done automatically for you by tooling and is checked as part of our CI pipeline.
As this can be automated, we will not go into detail about the formatting and linting rules.
Feel free to check out the `CONTIBUTING.md` file for more information on how to set up and work with the tools locally.
This document will instead focus on the content of the code and its aspects that are not covered by the tooling.

The content of this document is directly based on [PEP 8](https://peps.python.org/pep-0008/)
and [PEP 257](https://peps.python.org/pep-0257/).

## Python

In general, one should follow [PEP 8](https://peps.python.org/pep-0008/)
and [PEP 257](https://peps.python.org/pep-0257/), with the following exceptions and additions.

### Line Length

PEP 8 states that lines should be limited to 79 characters.
We use a line length of 88 characters instead of 79.
Programmers should still aim to keep their lines 79 characters or fewer.
However, by allowing a maximum of 88 characters, we can prevent unnecessary line breaks in some cases where this
significantly improves readability.

### F-strings

An f-string should only be used with simple expressions.
If an expression is too complex, it should be assigned to a variable first.

```python
# bad
f"The average is {(sum(values) / len(values)) if values else 0:.2f}"

# good
f"Hello {user.get_name()}"
f"Items: {', '.join(item.name for item in items)}"
f"Length: {len(items)}"

average = (sum(values) / len(values)) if values else 0
print(f"The average is {average:.2f}")
```

### Comments

Use single-line comments, possibly expanding over multiple lines, when code is not self-documenting:

```python
# bad
"""
A multiline
comment
"""

# good
# A multiline comment
# using single-line comments
```

_Note: do consider that rewriting the code to be self-documenting is often a better solution._

Use block comments to provide documentation for functions, classes, and modules. Always provide documentation for
functions and classes.

Use imperative language in comments.

For more information on how to write docstrings, see the [PEP 257](https://peps.python.org/pep-0257/).

In test docstrings, state the expected behaviour that each test demonstrates.
Do not include preambles such as “Tests that” or “Ensures that”.
