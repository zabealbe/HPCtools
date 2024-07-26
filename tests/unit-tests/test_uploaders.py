import pytest
from unittest.mock import patch, call
import os
from hpctools.uploaders import SFTPUploader
from hpctools.auths import SSHAuth
from hpctools.utils import MySSHClient

source = "mock-source-folder"
target = "/mywork/remote-mock-project"

auth = SSHAuth(
    hostname="hostname",
    username="username",
    key_filename="private/key/path",
)


@pytest.fixture
def mock_ssh_client(mocker):
    mock_connect = mocker.patch("hpctools.utils.MySSHClient.connect")
    mock_close = mocker.patch("hpctools.utils.MySSHClient.close")
    client = MySSHClient(auth)
    client.connect()

    yield client
    client.close()
    mock_connect.assert_called_once()
    mock_close.assert_called_once()


@pytest.fixture
def uploader(mock_ssh_client, mocker):
    mock_uploader = mocker.patch(
        "hpctools.uploaders.SFTPUploader.from_transport", return_value=mocker.Mock()
    )
    return mock_uploader(mock_ssh_client.get_transport())


def test_empty_directory(uploader):
    with patch("os.listdir", return_value=[]):
        with patch.object(uploader, "put") as mock_put:
            print("source: ", source)
            uploader.put_dir(source, target)
            mock_put.assert_not_called()


def test_blacklist_files(uploader):
    with patch("os.listdir", return_value=["file1.txt"]), patch(
        "os.path.isfile", return_value=True
    ), patch("os.path.join", side_effect=lambda *args: "/".join(args)), patch(
        "os.path.getmtime", return_value=10
    ):
        with patch.object(uploader, "put") as mock_put:
            uploader.put_dir(
                source, target, blacklist=["./mock-source-folder/file1.txt"]
            )
            mock_put.assert_not_called()
