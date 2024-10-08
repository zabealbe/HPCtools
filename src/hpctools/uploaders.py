import os
import abc

import paramiko
from . import auths as a


class Uploader(abc.ABC):
    @abc.abstractmethod
    def upload(self, source, target):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class SFTPUploader(Uploader, paramiko.SFTPClient):
    def upload(self, source, target, blacklist=[]):
        """
        Uploads the contents of the source directory to the target path. The
        target directory needs to exists. All subdirectories in source are
        created under target.
        """
        self.mkdir(target, ignore_existing=True)
        attrs = {attr.filename: attr for attr in self.listdir_attr(target)}
        for item in os.listdir(source):
            item_path = os.path.join(source, item)
            if item_path in blacklist:
                continue
            if os.path.isfile(item_path):
                # Filter out already up-to-date files. Does not work too well.
                if item not in attrs or attrs[item].st_mtime < os.path.getmtime(
                    item_path
                ):
                    self.put(item_path, os.path.join(target, item))
            else:
                self.mkdir(item_path, ignore_existing=True)
                self.upload(item_path, os.path.join(target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        """Augments mkdir by adding an option to not fail if the folder exists"""
        try:
            super().mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise


class RSYNCUploader(Uploader):
    def __init__(self, auth: a.SSHAuth):
        super().__init__()

        self.auth = auth

    def upload(self, source, target, blacklist=[]):
        ssh_command = f"ssh -p {self.auth.port}"

        if self.auth.key_filename is not None:
            ssh_command += f" -i {self.auth.key_filename}"

        if os.path.isdir(source):
            source = os.path.normpath(source) + os.path.sep

        exclude = " ".join([f"--exclude={item}" for item in blacklist])
        cmd = f"rsync -avz {exclude} -e '{ssh_command}' {source} {self.auth.username}@{self.auth.hostname}:{target}"
        print(cmd)

        os.system(cmd)

    def close(self):
        self.ssh_client.close()
