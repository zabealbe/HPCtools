from hpctools import runners

runner = runners.SSHRunner(
    workdir="/scratch/work/tiany4", # directory where the job will be run on the remote machine
    auth_kwargs={
        "hostname": "triton.aalto.fi",
        "username": "username",
        "key_filename": "private/key/path",
    },
)
import pkg_resources

# Access the template file path
template_path = pkg_resources.resource_filename('hpctools', 'templates/launch_scripts/job.bash.j2')

# Example of passing it to runner.run
runner.run(
    template=template_path,  # path to the template file
    template_args={
        # template-specific arguments
    }
)
