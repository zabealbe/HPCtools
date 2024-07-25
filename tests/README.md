Here are the steps to test hpctools in our development environment(can be created with `pip install -r requirements_dev.txt`):

1. Install hpctools from the root directory where `setup.py` is:
   Use `pip install -e .` to install the package to the dev environment in editable mode. This means that changes we make to the package are immediately available without reinstallation.
2. Instead of using relative paths, we should use absolute imports in test scripts based on the package structure.

3. Run test scripts:

```bash
pytest ./tests/unit ./tests/module ./tests/integration
```

Pytest will automatically discover and run all tests in those directories that match its naming conventions (typically files and functions starting with test\_).
