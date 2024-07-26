import os
import abc


class Auth(abc.ABC):
    pass


class SSHAuth(Auth):
    def __init__(
        self,
        username=None,
        key_filename=None,
        password=None,
        password_filename=None,
        hostname=None,
        port=22,
    ):
        self.username = username
        self.key_filename = key_filename
        self.password = password
        self.password_filename = password_filename
        self.hostname = hostname
        self.port = port

        if self.password_filename is not None:
            self.password_filename = os.path.expanduser(self.password_filename)

        if not self.password and self.password_filename:
            with open(self.password_filename, "r") as f:
                self.password = f.read()

        if self.key_filename:
            self.key_filename = os.path.expanduser(self.key_filename)

    def to_paramiko(self):
        kwargs = {}

        if self.username:
            kwargs["username"] = self.username
        if self.password:
            kwargs["password"] = self.password
        if self.key_filename:
            kwargs["key_filename"] = self.key_filename
        if self.hostname:
            kwargs["hostname"] = self.hostname
        if self.port:
            kwargs["port"] = self.port

        return kwargs
