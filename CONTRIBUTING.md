# Contributing Guidelines

Thank you for your interest in contributing to our project. Whether it's a bug report, new feature, correction, or additional
documentation, we greatly value feedback and contributions from our community.

Please read through this document before submitting any issues or pull requests to ensure we have all the necessary
information to effectively respond to your bug report or contribution.


## Reporting Bugs/Feature Requests

We welcome you to use the GitHub issue tracker to report bugs or suggest features.

When filing an issue, please check [existing open](https://github.com/aws-cloudformation/cfn-python-lint/issues), or [recently closed](https://github.com/aws-cloudformation/cfn-python-lint/issues?utf8=%E2%9C%93&q=is%3Aissue%20is%3Aclosed%20), issues to make sure somebody else hasn't already
reported the issue. Please try to include as much information as you can. Details like these are incredibly useful:

* A reproducible test case or series of steps
* The version of our code being used
* Any modifications you've made relevant to the bug
* Anything unusual about your environment or deployment

## Development Environment

1. You will need Python 3 >= 3.5. Verify which version you have by running `python --version`.

    > If you don't have it installed, download it [here](https://www.python.org/downloads/). When you do this, `pip` should be installed automatically.

1. Install `cfn-lint` from source by forking the repository and then doing a developer install:

    ```bash
    # fork the repository
    git clone https://github.com/<YOUR-USERNAME>/cfn-python-lint.git
    cd cfn-python-lint
    pip3 install -e .
    ```

1. Run `pip3 show cfn-lint`. The `Location` printed should be the folder from the step above.
1. You should now be able to modify the source code and see the changes immediately by running any of the `cfn-lint` commands. (Note: run `pip3 install -e .` again to re-install changes).

## Running the tests

The unit tests (and `pylint` for linting the Python code) are processed by [`tox`](https://tox.readthedocs.io/en/latest/). The configuration file is [tox.ini](/tox.ini).

Make sure Tox is installed and then run Tox by just calling it:

```bash
# Install Tox
$ pip install tox

# Run all tests (This command is also used when validating a Pull Request)
$ tox

# Run a specific test suite
$ tox -e py37 # Run all unit tests against Python 3.7
```
Tox test suites available:
* **py37**: Unit tests (Python 3.7)
* **py38**: Unit tests (Python 3.8)
* **py39**: Unit tests (Python 3.9)
* **py310**: Unit tests (Python 3.10)
* **py311**: Unit tests (Python 3.11)
* **style**: Python syntax check

## Contributing via Pull Requests
Contributions via pull requests are much appreciated. Before sending us a pull request, please ensure that:

1. You are working against the latest source on the *main* branch.
2. You check existing open, and recently merged, pull requests to make sure someone else hasn't addressed the problem already.
3. You open an issue to discuss any significant work - we would hate for your time to be wasted.

To send us a pull request, please:

1. Fork the repository.
2. Modify the source; please focus on the specific change you are contributing. If you also reformat all the code, it will be hard for us to focus on your change.
3. Ensure local tests pass.
4. Commit to your fork using clear commit messages.
5. Send us a pull request, answering any default questions in the pull request interface.
6. Pay attention to any automated CI failures reported in the pull request, and stay involved in the conversation.

GitHub provides additional document on [forking a repository](https://help.github.com/articles/fork-a-repo/) and
[creating a pull request](https://help.github.com/articles/creating-a-pull-request/).


## Finding contributions to work on
Looking at the existing issues is a great way to find something to contribute on. As our projects, by default, use the default GitHub issue labels (enhancement/bug/duplicate/help wanted/invalid/question/wontfix), looking at any ['help wanted'](https://github.com/aws-cloudformation/cfn-python-lint/labels/help%20wanted) issues is a great place to start.


## Code of Conduct
This project has adopted the [Amazon Open Source Code of Conduct](https://aws.github.io/code-of-conduct).
For more information see the [Code of Conduct FAQ](https://aws.github.io/code-of-conduct-faq) or contact
opensource-codeofconduct@amazon.com with any additional questions or comments.


## Security issue notifications
If you discover a potential security issue in this project we ask that you notify AWS/Amazon Security via our [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/). Please do **not** create a public GitHub issue.


## Licensing

See the [LICENSE](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/LICENSE) file for our project's licensing. We will ask you to confirm the licensing of your contribution.

We may ask you to sign a [Contributor License Agreement (CLA)](http://en.wikipedia.org/wiki/Contributor_License_Agreement) for larger changes.
