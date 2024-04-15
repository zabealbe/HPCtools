import os
import abc

class Auth(abc.ABC):
    pass

class SSHAuth(Auth):
    def __init__(
            self,
            username,
            hostname,
            port=22,
            key_filename=None,
            password=None,
            password_filename=None
    ):
        self.username = username
        self.hostname = hostname
        self.port = port
        self.key_filename = key_filename
        self.password = password
        self.password_filename = password_filename

        if not self.password and self.password_filename:
            with open(os.path.expanduser(self.password_filename)) as f:
                self.password = f.read()

        if self.key_filename:
            self.key_filename = os.path.expanduser(self.key_filename)

    def to_paramiko(self):
        return {
            "hostname": self.hostname,
            "port": self.port,
            "username": self.username,
            "key_filename": self.key_filename,
            "password": self.password,
        }
