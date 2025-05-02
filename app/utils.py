# app/utils.py
import subprocess
import os

def run_shell_command(command, cwd=None):
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True,
            cwd=cwd
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr

def file_size_in_megabytes(filepath):
    size = os.path.getsize(filepath) / (1024 * 1024)
    return size
