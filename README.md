<div align="center">
    <h1> :wrench: HPC Tools </h1>
</div>

Created by HPC users, for HPC users, to simplify and organize your workflows. Run parallel jobs, sweep configurations, and deploy in any environment with ease.

## *Currently Supported Environments
- Local Environment
- Slurm

To support more environments it is as easy as creating a new [launch script template](templates/launch_scripts), check [TUTORIAL.md](TUTORIAL.md) for an introduction.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installation

This project currently only supports Linux-based systems, and requires the following software to be installed:

-   Python 3.10+
-   OpenSSH
-   Rsync

You can install this project as a pypi package with the following command:

```bash
pip install git+https://github.com/zabealbe/HPCtools.git
```

### Tutorial

Now that the project is set up, go through the [TUTORIAL.md](TUTORIAL.md) file to learn how to use the tools in this repository, or directly check out some [examples](examples/).

## License

This repository is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

Derived works from the code under the `templates/` folder is excluded from the above and is licensed under the MIT License - see the [templates/LICENSE](templates/LICENSE) file for details.

We encourage users and organizations to use and modify the templates to suit their needs.
