Here are the steps to test hpctools in our development environment(can be created with `pip install -r requirements_dev.txt`):

1. Run `flit build` from the root directory where `pyproject.toml` is.
2. Run `pip install ./dist/hpctools-1.0.0-py3-none-any.whl` to install the package to the dev environment.
3. Instead of using relative paths, we should use absolute imports in test scripts based on the package structure.

4. Run test scripts:

```bash
pytest ./tests
```

Pytest will automatically discover and run all tests in the `tests` directory that match its naming conventions (typically files and functions starting with test\_).
