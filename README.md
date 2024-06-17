<div align="center">
    <h1> :wrench: HPC Tools </h1>
</div>

This repository contains a collection of useful tools and scripts for HPC users, they are designed to be simple and easily integrated into existing workflows.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

This project currently only supports Linux-based systems, and requires the following software to be installed:

-   Python 3.10+
-   OpenSSH
-   Rsync

OpenSSH and Rsync are typically installed by default on most Linux distributions, to verify, run the following commands:

```bash
$ ssh -V
OpenSSH_9.6p1, OpenSSL 3.2.1 30 Jan 2024
```

```bash
$ rsync --version
rsync  version 3.2.7  protocol version 31
```

### Installation

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
