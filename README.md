<div align="center">
    <h1> :wrench: HPC Tools </h1>
</div>

This repository contains a collection of useful tools and scripts for HPC users, they are designed to be simple and easily integrated into existing workflows.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.


### Prerequisites
This project currently only supports Linux-based systems, and requires the following software to be installed:
- Python 3.10+
- OpenSSH
- Rsync

OpenSSH and Rsync are typically installed by default on most Linux distributions, to verify, run the following commands:
```bash
$ ssh -V
OpenSSH_9.6p1, OpenSSL 3.2.1 30 Jan 2024
```

```bash
$ rsync --version
rsync  version 3.2.7  protocol version 31
Copyright (C) 1996-2022 by Andrew Tridgell, Wayne Davison, and others.
Web site: https://rsync.samba.org/
Capabilities:
    64-bit files, 64-bit inums, 64-bit timestamps, 64-bit long ints,
    socketpairs, symlinks, symtimes, hardlinks, hardlink-specials,
    hardlink-symlinks, IPv6, atimes, batchfiles, inplace, append, ACLs,
    xattrs, optional secluded-args, iconv, prealloc, stop-at, no crtimes
Optimizations:
    SIMD-roll, no asm-roll, openssl-crypto, no asm-MD5
Checksum list:
    xxh128 xxh3 xxh64 (xxhash) md5 md4 sha1 none
Compress list:
    zstd lz4 zlibx zlib none
Daemon auth list:
    sha512 sha256 sha1 md5 md4

rsync comes with ABSOLUTELY NO WARRANTY.  This is free software, and you
are welcome to redistribute it under certain conditions.  See the GNU
General Public Licence for details.
```

This project also requires some Python packages to be installed, they can be installed by running the following command:
```bash
pip install -r requirements.txt
```

### Installation
Once you have the prerequisites installed, clone the repository to your project folder, which should end up looing like this:
```
project_directory/
├── HPC-Tools/
└── ... other project files
```

### Tutorial
Now that the project is set up, go through the [TUTORIAL.md](TUTORIAL.md) file to learn how to use the tools in this repository, or directly check out some [examples](examples/).

## License
This repository is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

Derived works from the code under the `templates/` folder is excluded from the above and is licensed under the MIT License - see the [templates/LICENSE](templates/LICENSE) file for details.

We encourage users and organizations to use and modify the templates to suit their needs.