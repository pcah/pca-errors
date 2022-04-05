### `pca-errors`

## Contributing Guideline

First off, thanks for taking the time to contribute!

The following is a set of guidelines for contributing to `pca-errors` on GitHub. These are mostly guidelines, not rules. Use your best judgement, and feel free to propose changes to this document in a pull request.

### Table of contents

- [Contributing Guideline](#contributing-guideline)
  - [Table of contents](#table-of-contents)
- [How to contribute](#how-to-contribute)
  - [Reporting bugs](#reporting-bugs)
    - [Before submitting a bug report](#before-submitting-a-bug-report)
    - [How do I submit a bug report?](#how-do-i-submit-a-bug-report)
  - [Suggesting enhancements](#suggesting-enhancements)
    - [Before submitting an enhancement suggestion](#before-submitting-an-enhancement-suggestion)
    - [How do I submit an Enhancement suggestion?](#how-do-i-submit-an-enhancement-suggestion)
  - [Contributing to the code](#contributing-to-the-code)
    - [Local development](#local-development)
    - [Local testing](#local-testing)
    - [Pull requests](#pull-requests)

## How to contribute

### Reporting bugs

This section guides you through submitting a bug report for `pca-errors`.
Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

#### Before submitting a bug report

...**check that your issue does not already exist in the [issue tracker](https://github.com/pcah/pca-errors/issues)**.

> **Note:** If you find a **Closed** issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one.

#### How do I submit a bug report?

Bugs are tracked on the [issue tracker](https://github.com/pcah/pca-errors/issues) where you can create a new one and provide the following information by filling in [the bug report template](https://github.com/pcah/pca-errors/blob/master/docs/issue-templates/bug-report.md).

Explain the problem and include additional details to help maintainers reproduce the problem:

- **Use a clear and descriptive title** for the issue to identify the problem.
- **Describe the exact steps which reproduce the problem** in as many details as possible.
- **Provide specific examples to demonstrate the steps to reproduce the issue**. Include links to files or GitHub projects, or copy-paste-able snippets, which you use in those examples.
- **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
- **Explain which behavior you expected to see instead and why.**

Provide more context by answering these questions:

- **Did the problem start happening recently** (e.g. after updating to a new version of `pca-errors`) or was this always a problem?
- If the problem started happening recently, **can you reproduce the problem in an older version of `pca-errors`?** What's the most recent version in which the problem doesn't happen?
- **Can you reliably reproduce the issue?** If not, provide details about how often the problem happens and under which conditions it normally happens.

Include details about your configuration and environment:

- **Which version of `pca-errors` are you using?** You can get the exact version by running `python -c "import pca.packages.errors; print(pca.packages.errors.VERSION)"` in your terminal in the python environment or `poetry version` in the library repository.
- **Which Python version `pca-errors` has been installed for?** Execute the `python -V` to get the information.
- **What's the name and version of the OS you're using**?

### Suggesting enhancements

This section guides you through submitting an enhancement suggestion for `pca-errors`, including completely new features and minor improvements to existing functionality. Following these guidelines helps maintainers and the community understand your suggestion and find related suggestions.

#### Before submitting an enhancement suggestion

- **Check the [FAQs](https://github.com/pcah/pca-errors/blob/master/docs/FAQ.md)** for a list of common questions and problems.
- **Check that your idea of the enhancement does not already exist in the [issue tracker](https://github.com/pcah/pca-errors/issues)**.
- **Check that your idea is consistent with [the Principles](https://github.com/pcah/pca-errors/blob/master/docs/PRINCIPLES.md)** of the `pca-errors`.

#### How do I submit an Enhancement suggestion?

Enhancement suggestions are tracked on the [issue tracker](https://github.com/pcah/pca-errors/issues) where you can create a new one and provide the following information:

- **Use a clear and descriptive title** for the issue to identify the suggestion.
- **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
- **Provide specific examples to demonstrate the steps**.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why.

### Contributing to the code

#### Local development

You will need Poetry to start contributing on the `pca-errors` codebase.

You will first need to ensure you have `git`, `python` & `poetry` installed. Then, clone the repository using `git` and place yourself in its directory:

```bash
$ git clone git@github.com:pcah/pca-errors.git
$ cd pca-errors
```

Now, you will need to install the required dependency for `pca-errors` and be sure that the current tests are passing on the dev environment:

```bash
$ poetry install
```

To use a specific development environment, make sure you provide one by yourself. Supported environments include Pythons: 3.9, 3.8 and Pypy3 (for detailes, check [pyproject.toml](pyproject.toml)).

#### Local testing

- To run tests for all supported environments, run:

    ```bash
    $ poetry run tox
    ```

- To check a specific supported Python version, specify it after `-e` option:

    ```bash
    $ poetry run tox -e ENVIRONMENT
    ```

    where `ENVIRONMENT` becomes one of `py39|py38|py37|pypy3` (for detailes, check [tox.ini](tox.ini))).

- To check code styling rules, run linting container:

    ```bash
    $ poetry run pre-commit run -a
    ```

    `pca-errors` uses the [black](https://github.com/psf/black) coding formatter and you must ensure that your code follows it. If not, the CI will fail and your Pull Request will not be merged.

    Similarly, the import statements are sorted with [isort](https://github.com/timothycrosley/isort) and special care must be taken to respect it. If you don't, the CI will fail as well.

    Python code style is guarded with [flake8](https://flake8.pycqa.org/). Documentation style is guarded with [markdownlint](https://github.com/markdownlint/markdownlint). Both of them will fail your build, if you don't follow their rules.

    To make sure that you don't accidentally commit code that does not follow the coding style, you can install a pre-commit hook that will check that everything is in order:

    ```bash
    $ poetry run pre-commit install --install-hooks
    ```

    You can also run it anytime using:

    ```bash
    $ poetry run pre-commit run --all-files
    ```

- Your code must always be accompanied by corresponding tests, if tests are not present your code will not be merged.

#### Pull requests

- Fill in [the pull request template](https://github.com/pcah/pca-errors/blob/master/docs/issue-templates/pull-request.md).
- Be sure your commit messages repects [the commit message template](https://github.com/pcah/pca-errors/blob/master/docs/issue-templates/commit-message.md).
- Be sure that your pull request contains tests that cover the changed or added code.
- If your changes warrant a documentation change, the pull request must also update the documentation.
