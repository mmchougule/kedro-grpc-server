import platform
import shlex
import subprocess
import sys

if __name__ == "__main__":
    required_version = tuple(int(x) for x in sys.argv[1].strip().split("."))
    install_cmd = shlex.split(sys.argv[2])
    run_cmd = shlex.split(sys.argv[3])

    current_version = tuple(map(int, platform.python_version_tuple()[:2]))

    if current_version < required_version:
        print("Python version is too low, exiting")
        sys.exit(0)

    try:
        subprocess.run(run_cmd, check=True)
    except FileNotFoundError:
        subprocess.run(install_cmd, check=True)
        subprocess.run(run_cmd, check=True)
