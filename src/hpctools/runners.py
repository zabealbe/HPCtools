import os
from . import utils as u
from . import auths as a

class LAUNCH_COMMANDS(type):
    def __class_getitem__(cls, key):
        return LAUNCH_COMMANDS.MAP[key]

    SH = "chmod +x {launch_script_filename} && ./{launch_script_filename}"
    SLURM = "sbatch {launch_script_filename}"
    
    MAP = {
        "bash": SH,
        "sh": SH,
        "slurm": SLURM
    }

class TEMPLATING_ENGINES(type):
    def __class_getitem__(cls, key):
        return TEMPLATING_ENGINES.MAP[key]

    def j2(template, template_args):
        import jinja2

        # Custom undefined class that returns an empty string instead of raising an error
        class SilentUndefined(jinja2.Undefined):
            def _fail_with_undefined_error(self, *args, **kwargs):
                class EmptyString(str):
                    def __call__(self, *args, **kwargs):
                        return ""
                return EmptyString()

            __add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = \
                __truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = \
                __mod__ = __rmod__ = __pos__ = __neg__ = __call__ = \
                __getitem__ = __lt__ = __le__ = __gt__ = __ge__ = \
                __int__ = __float__ = __complex__ = __pow__ = __rpow__ \
                = _fail_with_undefined_error

        return jinja2.Template(
            open(template).read(),
            undefined=SilentUndefined
        ).render(
            **__builtins__,
            **template_args,
        )
    
    MAP = {
        "j2": j2
    }

class Runner:
    """
    Runner is an abstract class that defines the interface for running experiments.
    """
    def __init__(self,
            project_name: str=None,
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

        self.project_name = project_name

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

class SSHRunner(Runner):
    """
    SSHRunner is a runner that runs jobs on a remote host using SSH.
    """
    def __init__(self,
                 workdir,
                 auth: a.SSHAuth=None,
                 auth_kwargs: dict={},
        ):
        """
        Initializes the experiment runner.

        Args:
            workdir: The working directory on the remote host.
            auth: The authentication method to use.
            auth_kwargs: The arguments to pass to the authentication method.
        """
        super().__init__()
        if auth:
            self.auth = auth
        elif auth_kwargs:
            self.auth = a.SSHAuth(**auth_kwargs)
        else:
            raise ValueError("No authentication method provided")
        
        self.ssh_client = u.MySSHClient(self.auth)

        self.context = []
        self.context_blacklist = []
        self.workdir = workdir
        self.remote_experiment_dir = os.path.join(self.workdir, self.experiment_name)

        self.add_context(self.experiment_dir, self.remote_experiment_dir)

    def connect(self):
        print("Connecting to remote host")
        self.ssh_client.connect()

    def add_context(self, path, remote_path=None):
        path = os.path.abspath(path)

        if remote_path is None:
            remote_path = self.remote_experiment_dir
        if not os.path.isabs(remote_path):
            remote_path = os.path.join(self.remote_experiment_dir, remote_path)

        self.context.append((path, remote_path))
    
    def del_context(self, path):
        self.context_blacklist.append(path)

    def run(self, 
            template,
            template_args={},
            subexperiment_name=None,
            shell_template="bash -c 'cd {cwd} && {cmd}'",
            dry_run=False
        ):

        if self.ssh_client.get_transport() is None or not self.ssh_client.get_transport().is_active():
            self.connect()

        _, launch_script_ext, template_ext = template.rsplit(".", 2)
        launch_script_filename = (subexperiment_name + "." if subexperiment_name is not None else "") + f"launch.{launch_script_ext}"

        try:
            template_compile = TEMPLATING_ENGINES[template_ext]
            print(template_compile)
        except KeyError:
            raise ValueError(f"Unrecognized template extension: {template_ext}")
        
        # Add useful variables to the template arguments
        template_args.update(
            project_name=self.project_name,
            experiment_name=self.experiment_name,
            subexperiment_name=subexperiment_name,
        )

        # Compile the template
        launch_script = template_compile(template, template_args)

        # Write the launch script to the experiment directory
        with open(os.path.join(self.experiment_dir, launch_script_filename), "w") as f:
            f.write(launch_script)

        try:
            launch_command = LAUNCH_COMMANDS[launch_script_ext]
        except KeyError:
            raise ValueError(f"Unrecognized orchestrator extension: {launch_script_filename}")

        # Compile the launch command
        launch_command = shell_template.format(cwd=self.remote_experiment_dir, cmd=launch_command.format(launch_script_filename=launch_script_filename))
        print(f"Running {launch_command}")

        # Upload the context to the remote host
        print("Uploading context to remote host")
        for path, remote_path in self.context:
            print(f"Uploading {path} to {remote_path}")
            self.ssh_client.put_dir(
                path,
                remote_path,
                blacklist=self.context_blacklist
            )

        if dry_run:
            return

        # Run the launch script
        _, stdout, stderr = self.ssh_client.exec_command(launch_command)

        exitcode = stdout.channel.recv_exit_status()

        print(stdout.read().decode("utf-8"))
        print("\033[91m" + stderr.read().decode("utf-8") + "\033[0m")

class LocalRunner(Runner):
    """
    LocalRunner is a runner that runs jobs on the local host.
    """
    def __init__(self,
                 workdir
        ):
        """
        Initializes the experiment runner.

        Args:
            workdir: The working directory on the remote host.
        """
        super().__init__()

        self.context = []
        self.context_blacklist = []
        self.workdir = workdir
        self.remote_experiment_dir = os.path.join(self.workdir, self.experiment_name)

        self.add_context(self.experiment_dir, self.remote_experiment_dir)

    def add_context(self, path, remote_path=None):
        path = os.path.abspath(path)

        if remote_path is None:
            remote_path = self.remote_experiment_dir
        if not os.path.isabs(remote_path):
            remote_path = os.path.join(self.remote_experiment_dir, remote_path)

        self.context.append((path, remote_path))
    
    def del_context(self, path):
        self.context_blacklist.append(path)

    def run(self, 
            template,
            template_args={},
            subexperiment_name=None,
            shell_template="bash -c 'cd {cwd} && {cmd}'",
            dry_run=False
        ):

        _, launch_script_ext, template_ext = template.rsplit(".", 2)
        launch_script_filename = (subexperiment_name + "." if subexperiment_name is not None else "") + f"launch.{launch_script_ext}"

        try:
            template_compile = TEMPLATING_ENGINES[template_ext]
        except KeyError:
            raise ValueError(f"Unrecognized template extension: {template_ext}")
        
        # Add useful variables to the template arguments
        template_args.update(
            project_name=self.project_name,
            experiment_name=self.experiment_name,
            subexperiment_name=subexperiment_name,
        )

        # Compile the template
        launch_script = template_compile(template, template_args)

        # Write the launch script to the experiment directory
        with open(os.path.join(self.experiment_dir, launch_script_filename), "w") as f:
            f.write(launch_script)

        try:
            launch_command = LAUNCH_COMMANDS[launch_script_ext]
        except KeyError:
            raise ValueError(f"Unrecognized orchestrator extension: {launch_script_filename}")

        # Compile the launch command
        launch_command = shell_template.format(cwd=self.remote_experiment_dir, cmd=launch_command.format(launch_script_filename=launch_script_filename))
        print(f"Running {launch_command}")

        if dry_run:
            return

        # Run the launch script
        _, stdout, stderr = self.ssh_client.exec_command(launch_command)

        exitcode = stdout.channel.recv_exit_status()

        print(stdout.read().decode("utf-8"))
        print("\033[91m" + stderr.read().decode("utf-8") + "\033[0m")