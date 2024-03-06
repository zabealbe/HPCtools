import os
import utils as u
import jinja2

class Runner:
    """
    Runner is an abstract class that defines the interface for running experiments.
    """
    def __init__(self,
            experiment_name: str=None,
            subexperiment_name: str=None,
            experiment_dir: str=None
        ):
        """
        Initializes the experiment runner.

        Args:
            main: The path to the main experiment file.
            args: The arguments to pass to the experiment.
            name: The name of the experiment.
            experiment_dir: The directory to run the experiment from.
        """
        # If experiment is not specified, use the name of the experiment directory
        if experiment_dir is None:
            experiment_dir = os.getcwd()
        if experiment_name is None:
            experiment_name = os.path.basename(os.getcwd())

        self.experiment_dir = experiment_dir

        self.experiment_name = experiment_name
        self.subexperiment_name = subexperiment_name

    def run(self):
        raise NotImplementedError

class TritonRunner(Runner):
    """
    TritonRunner is a custom runner tailored to running experiments on the Triton cluster.
    """
    def __init__(self,
                 workdir,
                 **ssh_kwargs
        ):
        """
        Initializes the experiment runner.

        Args:
            workdir: The working directory on the remote host.
            hostname: The hostname of the remote host.
            port: The port to connect to.
            username: The username to use for authentication.
            password: The password to use for authentication.
            key_filename: The path to the private key file to use for authentication.
        """
        super().__init__()
        self.ssh_kwargs = ssh_kwargs
        self.ssh_client = u.MySSHClient(
            **self.ssh_kwargs
        )

        self.context = []
        self.workdir = workdir
        self.remote_experiment_dir = os.path.join(self.workdir, self.experiment_name)

        self.add_context(self.experiment_dir, self.remote_experiment_dir)

    def connect(self):
        print("Connecting to remote host")
        self.ssh_client.connect()

    def add_context(self, path, remote_path=None):
        if remote_path is None:
            remote_path = self.remote_experiment_dir
        if not os.path.isabs(remote_path):
            remote_path = os.path.join(self.workdir, remote_path)

        self.context.append((path, remote_path))
    
    def run(self, 
            template,
            template_args={},
            subexperiment_name=None
        ):

        if self.ssh_client.get_transport() is None or not self.ssh_client.get_transport().is_active():
            self.connect()

        slurmfile_name = "sbatch.slurm" if subexperiment_name is None else f"{subexperiment_name}.slurm"

        # Compile the template
        template = jinja2.Template(open(template).read())
        slurmfile = template.render(
            experiment_name=self.experiment_name,
            subexperiment_name=subexperiment_name,
            **__builtins__,
            **template_args
        )

        # Write the slurmfile to the experiment directory
        with open(os.path.join(self.experiment_dir, slurmfile_name), "w") as f:
            f.write(slurmfile)

        print("Uploading context to remote host")
        for path, remote_path in self.context:
            self.ssh_client.put_dir(path, remote_path)

        # Run the experiment through slurm
        _, stdout, stderr = self.ssh_client.exec_command(
            f"cd {self.remote_experiment_dir} && sbatch {slurmfile_name}"
        )

        exitcode = stdout.channel.recv_exit_status()

        print(stdout.read().decode("utf-8"))
        print("\033[91m" + stderr.read().decode("utf-8") + "\033[0m")