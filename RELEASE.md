# Release

This document details our approach to semantic versioning and how we release new versions of this project.

More information on the changes per release can be found in the [changelog](CHANGELOG.md).
More information on how to use this project can be found in the [README](README.md).

## Semantic Versioning

This project follows the principles of [semantic versioning](https://semver.org/).
The version number is in the format of `MAJOR.MINOR.PATCH` where:

- `MAJOR` is incremented when incompatible changes are made;
- `MINOR` is incremented when new features are added in a backwards-compatible manner, and
- `PATCH` is incremented when backwards-compatible bug fixes are made.

A major of `0` indicates that the project is still under initial development and that it should not be considered
stable.
Any version with a major of `0` may introduce breaking changes in minor versions.

## Release Process

We would like to maintain an Agile development workflow, which means that we will not have a fixed release schedule.

**The release process is as follows:**

1. If code changes are made, the maintainers of Octopus will decide if the changes are significant enough to warrant a new release;
2. If a release is warranted, the maintainers will increment the version number according to the semantic versioning rules;
3. If a release is warranted, the maintained will update the version in the `__about__.py` file;
4. If a release is warranted, the maintainers will create a Git tag and push it to the repository;
5. The maintainers will create a PR to merge the changes into the `main` branch.

When the PR is merged with the `main` branch, the release is considered complete.
If a release is warranted, automation will take care of creating a GitHub Release.
A Docker image will also automatically be built and pushed to the Docker Hub repository.
