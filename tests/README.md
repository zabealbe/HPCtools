Here are the steps to test hpctools in our development environment(can be created with `pip install -r requirements_dev.txt`):

1. Run `pip install -e .` to install hpctools in editable mode to the dev environment.
2. Instead of using relative paths, we should use absolute imports in test scripts based on the package structure.
3. Run test scripts:

```bash
pytest ./tests
```

Pytest will automatically discover and run all tests in the `tests` directory that match its naming conventions (typically files and functions starting with test\_).
