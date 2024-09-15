import pytest
from unittest.mock import patch, MagicMock
from hpctools.runners import SSHRunner
import pkg_resources
import os


# Mock the pkg_resources.resource_filename function
@pytest.fixture
def mock_resource_filename(mocker):
    return mocker.patch(
        "pkg_resources.resource_filename", return_value="/fake/path/job.bash.j2"
    )


# Mock the SSHRunner.run method to prevent actual SSH calls
@pytest.fixture
def mock_ssh_runner_run(mocker):
    return mocker.patch("hpctools.runners.SSHRunner.run")


def test_ssh_runner(mock_resource_filename, mock_ssh_runner_run):
    # Initialize the SSHRunner
    runner = SSHRunner(
        remote_workdir="/scratch/work/username/project",
        project_name="project",
        auth_kwargs={
            "hostname": "hostname",
            "username": "username",
            "key_filename": "private/key/path",
        },
    )
    template_path = pkg_resources.resource_filename(
        "hpctools", "templates/launch_scripts/job.bash.j2"
    )

    # Run the runner with the mocked template path
    runner.run(
        template=template_path,
        template_args={
            # template-specific arguments can be added here
        },
    )
    # Assertions to ensure methods were called correctly
    mock_resource_filename.assert_called_once_with(
        "hpctools", "templates/launch_scripts/job.bash.j2"
    )
    mock_ssh_runner_run.assert_called_once_with(
        template="/fake/path/job.bash.j2", template_args={}
    )
