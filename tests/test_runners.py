import pytest
import os
from hpctools.runners import LAUNCH_COMMANDS, TEMPLATING_ENGINES, Runner  # Ensure this import statement is correct based on your project structure

def test_launch_commands():
    assert LAUNCH_COMMANDS['bash'] == "chmod +x {launch_script_filename} && ./{launch_script_filename}"
    assert LAUNCH_COMMANDS['sh'] == "chmod +x {launch_script_filename} && ./{launch_script_filename}"
    assert LAUNCH_COMMANDS['slurm'] == "sbatch {launch_script_filename}"

def test_templating_engines_j2(tmp_path):
    # Create a temporary Jinja2 template file
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "hello.j2"
    p.write_text("Hello {{ name }}!")

    # Test rendering the template
    rendered = TEMPLATING_ENGINES['j2'](str(p), {'name': 'World'})
    assert rendered == "Hello World!"

    # Test the silent undefined
    rendered_undefined = TEMPLATING_ENGINES['j2'](str(p), {})
    assert rendered_undefined == "Hello !"

# def test_silent_undefined():
#     # Instantiate the SilentUndefined class and test its behavior
#     from runners     import TEMPLATING_ENGINES
#     undefined = TEMPLATING_ENGINES.SilentUndefined()
    
#     # Accessing an undefined attribute
#     assert undefined.some_random_attribute == ""
#     # Calling the undefined directly
#     assert undefined("any", arg=123) == ""
#     # Other operations
#     assert (undefined + "test") == ""

# Test for failure cases
def test_failures():
    with pytest.raises(KeyError):
        _ = LAUNCH_COMMANDS['nonexistent']
    with pytest.raises(KeyError):
        _ = TEMPLATING_ENGINES['nonexistent']


def test_runner_init_default():
    """
    Test that default initialization sets the correct experiment directory and name.
    """
    runner = Runner()
    assert runner.experiment_dir == os.getcwd(), "Default experiment_dir should be the current working directory"
    assert runner.experiment_name == os.path.basename(os.getcwd()), "Default experiment_name should be the basename of the current working directory"
    assert runner.project_name is None, "Default project_name should be None"
    assert runner.subexperiment_name is None, "Default subexperiment_name should be None"

def test_runner_init_custom():
    """
    Test initialization with custom parameters.
    """
    project_name = "ProjectX"
    experiment_name = "Experiment1"
    subexperiment_name = "Sub1"
    experiment_dir = "/fake/directory"

    runner = Runner(project_name=project_name, experiment_name=experiment_name, subexperiment_name=subexperiment_name, experiment_dir=experiment_dir)

    assert runner.project_name == project_name, "Project name should match the provided project name"
    assert runner.experiment_name == experiment_name, "Experiment name should match the provided experiment name"
    assert runner.subexperiment_name == subexperiment_name, "Subexperiment name should match the provided subexperiment name"
    assert runner.experiment_dir == experiment_dir, "Experiment directory should match the provided directory"

