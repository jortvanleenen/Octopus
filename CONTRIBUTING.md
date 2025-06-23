# Contributing

Thank you for wanting to contribute to this project!
To get started, be sure to have followed the installation instructions in the [README.md](README.md).
Then, read this document to understand how to contribute to this project.

## Creating an Issue

Before you start writing code, you should ensure a relevant issue exists.
This issue serves as a discussion point for the feature or bug you want to address.

Before you create a new issue for your work, check whether a similar issue already exists.
If a similar topic is found, you could create a sub-issue, or add a comment to the existing issue.

### New Issue

When a new issue is required, follow these steps:

1. Go to the _Issues_ tab and press "New issue";
2. Assign yourself, or any other relevant developer(s);
3. Assign a milestone if possible.

## How to Contribute

### Prepare Workspace

Follow the manual installation instructions in the [README.md](README.md) to set up your development environment.
Ensure you have the latest code by pulling the `develop` branch:

```bash
git checkout develop
git pull origin develop
```

### Create a Branch

Create a new branch (from the `develop` branch) according to the following schema:

- **Bug fix:** `bugfix/<issue number>-<short-description>`
- **Feature:** `feature/<issue number>-<short-description>`
- **Documentation:** `docs/<issue number>-<short-description>`
- **Refactor:** `refactor/<issue number>-<short-description>`
- **Test:** `test/<issue number>-<short-description>`

As an example, consider issue #42 to be related to fixing a logging issue in the benchmark runner.

```bash
git checkout -b bugfix/42-fix-logging-benchmark-runner
```

### Make your Changes

Make the necessary changes to the codebase.
Be sure to follow the best practices in ([CODING_STANDARDS.md](CODING_STANDARDS.md)).
When applicable, be sure to update the documentation.

### Commit and Push

We use a CI pipeline to check the code quality.
If your code is not correctly formatted or contains linting issues, the pipeline will fail.

To ensure your code adheres to the standards, it is recommended to run the linting and formatting checks locally and be
sure they pass.
To run the checks, execute:

```bash
ruff check --fix .
ruff format .
```

_Note: this can be automated to run on every commit by executing `pre-commit install` in your Python environment._

Commit your changes with a clear and concise commit message.
Ideally, the message is in the imperative language.

As an example, for the previously mentioned issue #42:

```bash
git commit -m "Fix missing logging in benchmark runner"
```

Push your changes to GitHub:

```bash
git push origin <your-branch-name>
```

## Create a Pull Request

A pull request (PR) is a request to merge your changes into the codebase.

1. Go to the _Pull Requests_ tab and press "New pull request";
2. Select the branch to merge and, normally, the `develop` branch;
3. Provide a clear title containing the branch name and write a concise description of the changes;
4. Make yourself an assignee;
5. Add any relevant labels;
6. Assign the correct _Milestone_ if applicable;
7. Link the PR to its corresponding issue(s).

If your PR is a work in progress, mark it as a draft to indicate that further changes are needed.

Once your PR is approved, an assignee (most often: you) is responsible for merging.

## How to Review

When reviewing PRs, please follow these steps:

1. **Check the PR**: Ensure that the title and description are clear and concise, contains the correct metadata (labels,
   etc.), and is linked to the correct issue(s);
2. **Review the code**:
    - **Functionality**: Confirm that the PR addresses the problem described in the issue;
    - **Documentation**: Ensure that any corresponding documentation is added (comments, docstrings, auxiliary files);
3. **Check the actions**: Review the status of all CI checks and ensure they pass;
4. **Request changes**: Request any changes you deem necessary;
5. **Approve the PR**: Once you are satisfied with the changes, approve the PR.
