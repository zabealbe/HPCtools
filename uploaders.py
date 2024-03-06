import os
import abc

import paramiko

class Uploader(abc.ABC):
    @abc.abstractmethod
    def put_dir(self, source, target):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

class SFTPUploader(Uploader, paramiko.SFTPClient):
    def put_dir(self, source, target):
        """
        Uploads the contents of the source directory to the target path. The
        target directory needs to exists. All subdirectories in source are
        created under target.
        """
        self.mkdir(target, ignore_existing=True)
        attrs = {attr.filename: attr for attr in self.listdir_attr(target)}
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                if item not in attrs or attrs[item].st_mtime < os.path.getmtime(
                    os.path.join(source, item)
                ):
                    self.put(os.path.join(source, item), os.path.join(target, item))
            else:
                self.mkdir(os.path.join(target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), os.path.join(target, item))

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
    def __init__(self, username, hostname, port=22, key_filename=None):
        super().__init__()

        self.username = username
        self.hostname = hostname
        self.port = port
        self.key_filename = key_filename

    def put_dir(self, source, target):
        ssh_command = f"ssh -p {self.port}"
        if self.key_filename is not None:
            ssh_command += f" -i {self.key_filename}"
        os.system(f"rsync -avz -e '{ssh_command}' {source}/ {self.username}@{self.hostname}:{target}")

    def close(self):
        self.ssh_client.close()


