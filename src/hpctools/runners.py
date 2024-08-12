import os
import re
import subprocess
from .utils import MySSHClient, dotdict
from .auths import SSHAuth

DEBUG = False


class LAUNCH_COMMANDS(type):
    def __class_getitem__(cls, key):
        return LAUNCH_COMMANDS.MAP[key]

    SH = "chmod +x {launch_script_filename} && ./{launch_script_filename}"
    SLURM = "sbatch {launch_script_filename}"

    MAP = {
        "bash": SH,
        "sh": SH,
        "slurm": SLURM,
    }


class TEMPLATING_ENGINES(type):
    def __class_getitem__(cls, key):
        return TEMPLATING_ENGINES.MAP[key]

    def j2(template, **template_kwargs):
        import jinja2

        # Custom undefined class that returns an empty string instead of raising an error
        class SilentUndefined(jinja2.Undefined):
            def _fail_with_undefined_error(self, *args, **kwargs):
                class EmptyString(str):
                    def __call__(self, *args, **kwargs):
                        return ""

                return EmptyString()

            __add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = (
                __truediv__
            ) = __rtruediv__ = __floordiv__ = __rfloordiv__ = __mod__ = __rmod__ = (
                __pos__
            ) = __neg__ = __call__ = __getitem__ = __lt__ = __le__ = __gt__ = __ge__ = (
                __int__
            ) = __float__ = __complex__ = __pow__ = __rpow__ = (
                _fail_with_undefined_error
            )

        return jinja2.Template(open(template).read(), undefined=SilentUndefined).render(
            **template_kwargs,
        )

    MAP = {
        "j2": j2,
    }


class Runner:
    """
    Runner is an abstract class that defines the interface for running experiments.

    The `Runner` class provides a common interface for running experiments in a project.
    It handles the creation of launch files, the execution of the experiments, and the management of the experiment context (files and directories).
    """

    # The `LAUNCH_COMMANDS` dictionary defines the commands used to launch experiments for different types of job schedulers (e.g., Bash, Slurm).
    # The keys in this dictionary represent the file extension of the launch file, and the values are the corresponding launch commands.
    LAUNCH_COMMANDS = {
        "bash": "chmod +x {launch_file_name} && (./{launch_file_name} &> /dev/null & disown)",
        "sh": "chmod +x {launch_file_name} && (./{launch_file_name} &> /dev/null & disown)",
        "slurm": "sbatch {launch_file_name}",
    }

    def __init__(
        self,
        project_name: str,
        experiment_dir: str = None,
        experiment_name: str = None,
        environment: dict = None,
    ):
        """
        Initializes the experiment runner.

        Args:
            project_name (str): The name of the project.
            experiment_dir (str, optional): The directory containing the necessary configuration and files for the experiment. If not provided, the current working directory will be considered the experiment directory.
            experiment_name (str, optional): The name of the experiment. If not provided, it will default to the basename of `experiment_dir`.
            environment (dict, optional): A dictionary of environment variables to be used during the experiment. If not provided, an empty dictionary will be used.
        """

        self.project_name = project_name

        # If experiment_dir is not specified, use the name of the experiment directory
        if experiment_dir is None:
            experiment_dir = os.getcwd()
        self.experiment_dir = experiment_dir
        self.experiment_rundir = self.experiment_dir

        # If experiment_name is not specified, use the basename for experiment_dir
        if experiment_name is None:
            experiment_name = os.path.basename(self.experiment_dir)
        self.experiment_name = experiment_name

        if environment is None:
            environment = {}
        self.environment = environment

        self.context = []
        self.context_blacklist = []

    def add_context(self, source_path, target_path=None):
        """
        Adds a file or directory to the experiment context.

        The `add_context()` method allows you to specify a source path and an optional target path. The source path is the path to the file or directory that you want to include in the experiment context. The target path is the path where the file or directory will be copied in the experiment run directory.

        If the target path is not specified, the file or directory will be copied to the experiment run directory with the same name as the source path.

        Args:
            source_path (str): The path to the file or directory to be included in the experiment context.
            target_path (str, optional): The path where the file or directory will be copied in the experiment run directory.
        """
        source_path = os.path.abspath(source_path)

        if target_path is None:
            target_path = self.experiment_rundir
        if not os.path.isabs(target_path):
            target_path = os.path.join(self.experiment_rundir, target_path)

        self.context.append((source_path, target_path))

    def del_context(self, path):
        """
        Removes a file or directory from the experiment context.

        The `del_context()` method allows you to specify a path to a file or directory that should be excluded from the experiment context. This can be useful if you need to remove a file or directory that was previously added to the context.

        Args:
            path (str): The path to the file or directory to be removed from the experiment context.
        """
        self.context_blacklist.append(path)

    def run(
        self,
        template,
        template_args={},
        run_name=None,
        dry_run=False,
    ):
        """
        Runs the experiment using the specified template and arguments.

        The `run()` method is responsible for generating the launch file, executing the experiment, and performing any necessary cleanup.

        Args:
            template (str): The path to the template file used to generate the launch file.
            template_args (dict, optional): A dictionary of arguments to be passed to the template compiler.
            run_name (str, optional): The name of the experiment run. If not provided, a default name will be generated.
            dry_run (bool, optional): If True, the launch command will be printed but not executed.

        Returns:
            A `dotdict` object containing the job attributes.
        """
        self.run_before()

        _, launch_file_ext, template_ext = template.rsplit(".", 2)

        launch_command = self.__class__.LAUNCH_COMMANDS.get(launch_file_ext, None)
        if launch_command is None:
            raise ValueError(f"Unrecognized launch file of type {launch_file_ext}")

        template_compiler = TEMPLATING_ENGINES.get(template_ext, None)
        if template_compiler is None:
            raise ValueError(f"Unrecognized template extension: {template_ext}")

        # Generate the launch file name
        launch_file_name = ".".join(
            filter(
                None,
                [
                    "launch",
                    run_name,
                    launch_file_ext,
                ],
            )
        )
        launch_file_name = os.path.join(self.experiment_dir, launch_file_name)

        # Generate the job name
        job_name = "/".join(
            filter(
                None,
                [
                    self.project_name,
                    self.experiment_name,
                    run_name,
                ],
            )
        )
        # Allow only certain characters
        pattern = re.compile(
            "([^"
            # \U0001F9EA # 🧪
            "A-Za-z"  # Leters
            "0-9"  # Numbers
            "\-._\/"  # Other symbols
            "]+)",
            flags=re.UNICODE,
        )
        job_name = re.sub(pattern, "", job_name)

        # Compile the launch file template
        launch_file = template_compiler(
            template,
            # Useful variables
            **__builtins__,
            project_name=self.project_name,
            experiment_name=self.experiment_name,
            run_name=run_name,
            # Actual args
            **template_args,
        )

        # Write the launch file to disk
        with open(launch_file_name, "w+") as f:
            f.write(launch_file)

        # Compile the launch command
        launch_command.format(
            launch_file_name=launch_file_name,
        )

        print(f"Launch command: {launch_command}")

        self.sync_context()

        if dry_run:
            print("Dry run: Launch command not executed")
        else:
            # Run the launch command
            stdout, stderr, exitcode = self.exec(launch_command)

            print(stdout.read().decode("utf-8"))
            print("\033[91m" + stderr.read().decode("utf-8") + "\033[0m")

        # Cleanup
        if not DEBUG:
            os.remove(launch_file_name)

        self.run_after()

        job = dotdict(name=job_name)

        return job

    def exec(self):
        """
        Executes the specified command in the target environment of the runner.

        Args:
            command (str): The command to be executed.

        Returns:
            A tuple containing the stdout, stderr, and exit code of the executed command.
        """
        pass

    def sync_context(self):
        """
        Synchronizes the experiment context.

        This method is responsible for copying the files and directories specified in the experiment context to the experiment run directory. It also excludes any files or directories specified in the `context_blacklist`.
        """
        pass

    def run_before(self):
        """
        Performs any necessary setup tasks before running the experiment.

        This method can be overridden by subclasses to perform any necessary setup tasks before the experiment is run.
        """
        pass

    def run_after(self):
        """
        Performs any necessary cleanup tasks after running the experiment.

        This method can be overridden by subclasses to perform any necessary cleanup tasks after the experiment has been run.
        """
        pass


class SSHRunner(Runner):
    """
    SSHRunner is a runner that runs jobs on a remote host using SSH.
    """

    def __init__(
        self,
        remote_workdir,
        *args,
        auth: SSHAuth = None,
        auth_kwargs: dict = {},
        **kwargs,
    ):
        """
        Initializes the experiment runner.

        Args:
            remote_workdir (str): The working directory on the remote host.
            *args: Positional arguments passed to the parent `Runner` class.
            auth (SSHAuth, optional): The authentication method to use. If not provided, `auth_kwargs` must be specified.
            auth_kwargs (dict, optional): The arguments to pass to the authentication method. If `auth` is provided, this argument is ignored.
            **kwargs: Keyword arguments passed to the parent `Runner` class.
        """
        super().__init__(*args, **kwargs)
        if auth:
            self.auth = auth
        elif auth_kwargs:
            self.auth = SSHAuth(**auth_kwargs)
        else:
            raise ValueError("No authentication method provided")

        self.ssh_client = MySSHClient(self.auth)

        self.experiment_rundir = os.path.join(remote_workdir, self.experiment_name)

        self.add_context(self.experiment_dir, self.experiment_rundir)

    def connect(self):
        if (
            self.ssh_client.get_transport() is None
            or not self.ssh_client.get_transport().is_active()
        ):
            print("Connecting to remote host")
            self.ssh_client.connect()
        else:
            print("Already connected to remote host")

    def sync_context(self):
        print("Uploading context to remote host")
        for local_path, remote_path in self.context:
            print(f"Uploading {local_path} to {remote_path}")
            self.ssh_client.upload(
                local_path, remote_path, blacklist=self.context_blacklist
            )

    def exec(self, cmd, shell="bash -c", environment={}):
        environment = self.environment.update(environment)
        environment = " ".join([f"{k}={v}" for k, v in environment.items()])
        if environment:
            environment = f"export {environment};"

        cmd = f"{shell} '{environment} {cmd}'"

        _, stdout, stderr = self.ssh_client.exec_command(cmd)

        exitcode = stdout.channel.recv_exit_status()

        return stdout, stderr, exitcode

    def run_before(self):
        # Initialize ssh connection
        self.connect()


class LocalRunner(Runner):
    """
    LocalRunner is a runner that runs jobs on the local host.
    """

    def add_context(self, source_path, target_path=None):
        source_path = os.path.abspath(source_path)

        if target_path is None:
            target_path = self.experiment_dir
        if not os.path.isabs(target_path):
            target_path = os.path.join(self.experiment_dir, target_path)

        self.context.append((source_path, target_path))

    def del_context(self, path):
        self.context_blacklist.append(path)

    def exec(self, cmd, environment={}):
        environment = self.environment.update(environment)

        process = subprocess.Popen(
            cmd,
            shell=True,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        exitcode = process.wait()

        return stdout, stderr, exitcode
