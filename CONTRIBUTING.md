# How to contribute

We would love to accept contributions from our colleagues.
If you have additional ideas for Kedro-Server functionality, questions or workflows you particularly struggle with, please open a GitHub issue with the label `idea`. You can submit an issue [here](https://github.com/mmchougule/kedro-grpc-server/issues).

## Contributing fixes to existing functionality

To contribute, please fork this repository and create a pull request against the `develop` branch.

We recommend first to get in touch with a member of the core team who will help
you understand and adhere to our coding guidelines. Furthermore, they will
help find the right place to contribute whether it is `core` or `contrib`.

GitHub will suggest reviewers automatically, you should make sure that at least
two people are selected to review your change.

## Guidelines and standards

We adhere to the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guid,
and we use [`black`](https://github.com/ambv/black) as our code formatter.

We do a lot of automated checks, so please make sure to check `circleci` outputs for
failed builds.

To speed up this process, we also provide a `Makefile` that automates testing and linting.
Your build will be green if all of the following commands succeed:

```bash
  make lint      # run linters
  make legal     # run legal checks
  make test      # run tests

  # circleci build # run build if circleci is installed
```

Also, we use [pre-commit](https://pre-commit.com) hooks for the repository to run the checks automatically.
It can all be installed using the following command:

```bash
pip install -r test_requirements.txt
make install-test-requirements
make install-pre-commit
```

We use a branching model that helps us keep track of branches in a logical, consistent way, it involves prepending the branch name with one of four prefixes:

* `contrib` e.g. the full branch name of `contrib/my_awesome_contrib_module`. This is intended to be used when you contribute a contrib module, or make an update to one
* `feature` e.g. the full branch name of `feature/add_feature_to_core`. This is intended for when adding a new feature to the core framework
* `fix` e.g. the full branch name of `fix/showstopper_core_bug`. This is intended for when you are making a fix to something in the core framework
* `release` e.g. the full branch name of `release/full_version_no`. This is intended for release branches (minor, major, rc etc.)

Branch names, as defined above, are suffixed by the ticket number when a ticket exists. e.g.  `fix/showstopper_bug(#CAI-123)`

## Hints on pre-commit usage
The checks will automatically run on all the changed files on each commit.
Even more extensive set of checks (including the heavy set of `pylint` checks)
will run before the push.

The pre-commit/pre-push checks can be omitted by running with `--no-verify` flag, as per below:

```bash
git commit --no-verify <...>
git push --no-verify <...>
```
(`-n` alias works for `git commit`, but not for `git push`)

All checks will run during CI build, so skipping checks on push will
not allow you to merge your code with failing checks.

You can uninstall the pre-commit hooks by running
```bash
make uninstall-pre-commit
```
`pre-commit` will still be used by `make lint`, but will install the git hooks.
