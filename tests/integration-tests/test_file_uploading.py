from hpctools import auths as a
from hpctools import utils as u
from hpctools.uploaders import *
from unittest.mock import patch, call
import pytest
import os
from pathlib import Path

source = './mock-source-folder'
target = f"/scratch/work/{os.getenv('SSH_USERNAME')}/mock-project"

auth = a.SSHAuth(hostname=os.getenv("SSH_HOSTNAME"),
                 username=os.getenv("SSH_USERNAME"),
                 key_filename=os.getenv("SSH_KEY_FILENAME"),
                 )

@pytest.fixture(scope="module")
def ssh_client():
    client = u.MySSHClient(auth)
    client.connect()
    yield client
    client.close()

@pytest.fixture
def uploader(ssh_client):
    return SFTPUploader.from_transport(ssh_client.get_transport())

# uploader = SFTPUploader.from_transport(ssh_client.get_transport())

# Test function for empty directory
def test_empty_directory(uploader):
    with patch("os.listdir", return_value=[]):
        with patch.object(uploader, 'put') as mock_put:
            print("source: ", source)
            uploader.put_dir(source, target)
            mock_put.assert_not_called()

def test_file_uploading(uploader):
    with patch("os.listdir", return_value=["file1.txt", "file2.txt"]), \
         patch("os.path.isfile", side_effect=lambda x: True), \
         patch("os.path.join", side_effect=lambda *args: '/'.join(args)), \
         patch("os.path.getmtime", return_value=10):
        with patch.object(uploader, 'put') as mock_put, \
             patch.object(uploader, 'listdir_attr', return_value=[]):
            uploader.put_dir(source, target)
            expected_calls = [
                call(f"{source}/file1.txt", f"{target}/file1.txt"),
                call(f"{source}/file2.txt", f"{target}/file2.txt")
            ]
            mock_put.assert_has_calls(expected_calls, any_order=True)

def test_blacklist_files(uploader):
    with patch("os.listdir", return_value=["file1.txt"]), \
         patch("os.path.isfile", return_value=True), \
         patch("os.path.join", side_effect=lambda *args: '/'.join(args)), \
         patch("os.path.getmtime", return_value=10):
        with patch.object(uploader, 'put') as mock_put:
            uploader.put_dir(source, target, blacklist=["./mock-source-folder/file1.txt"])
            mock_put.assert_not_called()

def test_directory_creation(uploader):
    with patch("os.listdir", side_effect=lambda path: ["dir1"] if path == source else []), \
         patch("os.path.isfile", return_value=False), \
         patch("os.path.isdir", return_value=True), \
         patch("os.path.join", side_effect=lambda *args: '/'.join(args)), \
         patch.object(uploader, 'listdir_attr', return_value=[]), \
         patch.object(uploader, 'put') as mock_put, \
         patch.object(uploader, 'mkdir') as mock_mkdir:
        uploader.put_dir(source, target)
        mock_mkdir.assert_called_with(f"{target}/dir1", ignore_existing=True)

def test_mkdir_ignore_existing(uploader):
    with patch.object(uploader, 'mkdir', wraps=uploader.mkdir) as mock_mkdir:
        # Simulate IOError when directory already exists
        with patch('paramiko.SFTPClient.mkdir', side_effect=IOError):
            # Call mkdir with ignore_existing=True
            uploader.mkdir(target, ignore_existing=True)
            # Ensure IOError was caught and ignored
            mock_mkdir.assert_called_with(target, ignore_existing=True)
            # Call mkdir with ignore_existing=False and check if IOError is raised
            with pytest.raises(IOError):
                uploader.mkdir(target, ignore_existing=False)


@pytest.fixture
def rsync_uploader():
    return RSYNCUploader(auth)

def test_rsync_call(rsync_uploader):
    source_path = Path(source)
    source_path.mkdir(parents=True, exist_ok=True)
    (source_path / "file.txt").write_text("data")

    with patch('os.system') as mock_os:
        rsync_uploader.put_dir(str(source_path), target, blacklist=["ignore.txt"])
        mock_os.assert_called_once_with(
            "rsync -avz -e 'ssh -p 22 -i {0}' --exclude=ignore.txt {1}/ {2}@{3}:{4}".format(
                os.getenv("SSH_KEY_FILENAME"),
                str(source_path), 
                os.getenv('SSH_USERNAME'), 
                os.getenv('SSH_HOSTNAME'),
                target
            )
        )
        