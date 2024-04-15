# Tutorial

The main idea behind this project is to provide a set of tools, mostly python classes and functions, that can be easily integrated into existing workflows or to build your own. We provide example workflows in the form of jupyter notebooks in the [examples](examples/) folder.

## Uploader
The uploader's job is to transfer files from one location to another, typically from the local machine to the remote machine. At the moment, there are two uploaders available: the SFTPUploder and the RsyncUploader.

If you are using a Runner, you do not need to use the uploaders directly, as the runners will handle the file transfer for you. Check the [Runner](#runner) section for more information on how to use the runners.

### SFTP Uploader
The SFTPUploader uses the paramiko library and the SFTP protocol to transfer files from the local machine to the remote machine. It is typically slower than the RsyncUploader, as it does not support delta transfers nor compression.
### Rsync Uploader
The RsyncUploader uses the rsync command-line tool to transfer files from the local machine to the remote machine. When possible, it is recommended to use the RsyncUploader.

## Runner
The runner's job is to submit jobs to the target system. At the moment, there are two runners available: the SSHRunner and the LocalRunner.

Internally, the runner completes the following steps:
1. Compile the [launch script template](#launch-script) using the provided arguments.
2. Transfer the compiled launch script and any additional files to the target destination.
3. Submit the job to the target system.

### SSH Job Runner
The SSH job runner is a tool that allows users to submit jobs to a remote machine via SSH, it is typically used to launch slurm jobs from the HPC cluster login node.

Sample usage:
```python
import runners

runner = runners.SSHRunner(
    workdir="/home/user/workspace/example_project", # directory where the job will be run on the remote machine
    auth_kwargs={
        "hostname": "example.com",
        "username": "user",
        "key_filename": "/path/to/private/key",
    },
)

runner.run(
    template="(HPC Tools directory)/templates/launch_scripts/job.bash.j2", # path to the template file
    template_args={
        # template-specific arguments
    }
)
```

### Local Job Runner
The local job runner is meant to be used for running jobs on the local machine.

Sample usage:
```python
import runners

runner = runners.LocalRunner(
    workdir="/home/user/workspace/example_project", # directory where the job will be run
)

runner.run(
    template="(HPC Tools directory)/templates/launch_scripts/job.bash.j2", # path to the template file
    template_args={
        # template-specific arguments
    }
)
```

## Launch Script
The launch script is a executable file that is run on the target system, this script will set up the environment and run the job. The launch script is compiled from a template file, typically a Jinja2 template. Although the provided templates should be general enought to adapt to most situations, it is encouraged for users to create their own launch script templates to suit their needs, checkout the available [templates](templates/launch_scripts) for examples.

The template file name should take the form:
```bash
"*.{launch_script_type}.{template_extension}"
```
where:
- `*`                  can be anything to identify the template
- `launch_script_type` is the type of the launch script, and tells the runner how to run the script
- `template_extension` is template file extension, and tells the runner how to compile the template

examples:
```
job.bash.j2
 │   │   └──────── compile with jinja2
 │   └──────────── run as bash script
 └──────────────── serial job 
```
```
arrayjob.slurm.j2
   │       │   └── compile with jinja2
   │       └────── run as slurm script
   └────────────── parallel job 
```