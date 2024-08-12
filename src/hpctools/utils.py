import paramiko
import os
from paramiko.config import SSH_PORT
from functools import reduce
from .uploaders import Uploader, SFTPUploader, RSYNCUploader
from .auths import *


class dotdict(dict):
    """
    Dot notation access to dictionary attributes
    """

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class MySSHClient(paramiko.SSHClient):
    def __init__(self, auth: SSHAuth):
        super().__init__()

        self.auth = auth

        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        super().connect(**self.auth.to_paramiko())

    def mkdir(self, path):
        self.exec_command(f"mkdir -p {path}")

    def put_dir(self, source, target, blacklist=[], uploader="rsync"):
        if uploader == "sftp":
            SFTPUploader.from_transport(self.get_transport()).put_dir(
                source, target, blacklist
            )
        elif uploader == "rsync":
            RSYNCUploader(self.auth).put_dir(source, target)
        elif isinstance(uploader, Uploader):
            uploader.put_dir(source, target, blacklist)


class GridConfig:
    def __init__(self, config: dict, config_names: list = None):
        self.config = config
        self.config_names = config_names
        self._idx = 0

    def get_dimenstions(self):
        dim_sizes = []
        for k, v in self.config.items():
            if isinstance(v, list):
                dim_sizes.append(len(v))
            else:
                dim_sizes.append(1)
        return dim_sizes

    def size(self):
        """Returns the number of configurations in the grid"""
        if len(self.get_dimenstions()) == 0:
            return 1
        return reduce(lambda x, y: x * y, self.get_dimenstions())

    def idx_to_dim_ids(self, idx):
        dim_ids = {}
        for k, v in self.config.items():
            if isinstance(v, list):
                dim_ids[k] = idx % len(v)
                idx = idx // len(v)
        return dim_ids

    def get_config(self, grid_idx=0, to_args=False):
        if self.size() == 0:
            return self.config
        if grid_idx >= self.size():
            raise ValueError("Grid index out of bounds")

        dim_ids = self.idx_to_dim_ids(grid_idx)
        config = {}

        for i, (k, v) in enumerate(self.config.items()):
            if isinstance(v, list):
                v = v[dim_ids[k]]

            if isinstance(k, tuple):
                for k_, v_ in zip(k, v):
                    config[k_] = v_

            else:
                config[k] = v

        if to_args:
            config = dict_to_args(config)

        return config

    def flatten(self, **kwargs):
        """
        Returns a list of all possible configurations
        """
        configs = []
        for i in range(self.size()):
            configs.append(self.get_config(i, **kwargs))
        return configs

    def __next__(self):
        if self._idx >= self.size():
            raise StopIteration
        else:
            config = self.get_config(self._idx)
            self._idx += 1
            return config

    def __iter__(self):
        self._idx = 0
        return self

    def __len__(self):
        return self.size()


def dict_to_args(dictionary, prefix="--", separator=" ", join=" "):
    args = []
    for k, v in dictionary.items():
        if isinstance(v, bool):
            if v:  # --foo
                args.append(f"{prefix}{k}")
        elif isinstance(v, str):  # --foo="bar"
            if "'" in v or '"' in v:
                raise ValueError(
                    f"The string {v} contains quotes, which is not supported"
                )
            v = "'" + v + "'"
            args.append(rf"{prefix}{k}{separator}{v}")
        elif isinstance(v, int):
            args.append(f"{prefix}{k}{separator}{v}")
        elif isinstance(v, float):
            args.append(f"{prefix}{k}{separator}{v}")
        else:
            raise ValueError(f"Unsupported type {type(v)} for argument {k}")
    return join.join(args)


def dict_to_slurm_args(dictionary):
    return dict_to_args(dictionary, prefix="#SBATCH --", separator="=", join="\n")


def flatten_names(names, join="_"):
    dims = []
    size = 1
    for l in names:
        if isinstance(l, list):
            dim_size = len(l)
            dims.append(dim_size)
            size *= dim_size
        else:
            dims.append(1)

    flattened_names = []
    for i in range(size):
        dim_ids = []
        flattened_names.append([])
        for dim_id, dim_size in enumerate(dims):
            dim_ids.append(i % dim_size)
            i = i // dim_size
            dim = names[dim_id]
            if isinstance(dim, list):
                flattened_names[-1].append(dim[dim_ids[-1]])
            else:
                flattened_names[-1].append(dim)

        flattened_names[-1] = join.join(flattened_names[-1])

    return flattened_names
