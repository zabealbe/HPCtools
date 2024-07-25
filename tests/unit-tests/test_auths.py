import pytest
from hpctools.auths import SSHAuth
from unittest.mock import mock_open, patch
import os

def test_ssh_auth_initialization():
    auth = SSHAuth("user", "host")
    assert auth.username == "user"
    assert auth.hostname == "host"
    assert auth.port == 22
    assert auth.key_filename is None
    assert auth.password is None
    assert auth.password_filename is None

def test_ssh_auth_with_password():
    auth = SSHAuth("user", "host", password="mypassword")
    assert auth.password == "mypassword"

def test_ssh_auth_with_key_filename():
    auth = SSHAuth("user", "host", key_filename="~/.ssh/id_rsa")
    assert auth.key_filename == os.path.expanduser("~/.ssh/id_rsa")

def test_ssh_auth_with_password_filename():
    mock_file_content = "secret"
    with patch("builtins.open", mock_open(read_data=mock_file_content)) as mock_file:
        auth = SSHAuth("user", "host", password_filename="~/secret.txt")
        mock_file.assert_called_once_with(os.path.expanduser("~/secret.txt"))
        assert auth.password == "secret"

def test_to_paramiko_output():
    auth = SSHAuth("user", "host", port=2222, key_filename="~/.ssh/id_rsa", password="mypassword")
    expected = {
        "hostname": "host",
        "port": 2222,
        "username": "user",
        "key_filename": os.path.expanduser("~/.ssh/id_rsa"),
        "password": "mypassword",
    }
    assert auth.to_paramiko() == expected
