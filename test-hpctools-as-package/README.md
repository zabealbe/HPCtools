Here are the steps to test hpctools as an installable package:

1. Create a python virtual environment:

```bash
python -m venv myenv
source ./myenv/bin/activate
```

2. Install hpctools from git source:

```bash
pip install paramiko jinja2
pip install git+https://github.com/YuTian8328/HPCtools.git@yu-dev
```

3. Run test code after modify it with your own settings:

```bash
python test_runner.py
```
