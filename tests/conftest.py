import os
import subprocess
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner
from kedro.context import KedroContext, load_context


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner


@pytest.fixture
def dummy_kedro_config(cli_runner):
    config = {
        "project_name": "Dummy project",
        "repo_name": "dummy-project",
        "python_package": "dummy_project",
        "include_example": True,
        "output_dir": os.getcwd(),
    }

    config_path = Path("config.yml")

    with config_path.open("w", encoding="utf-8") as file_:
        yaml.dump(config, file_)

    return config_path.resolve()


@pytest.fixture
def dummy_kedro_project(dummy_kedro_config):
    cwd_ = os.getcwd()
    subprocess.check_call(["kedro", "new", "-c", str(dummy_kedro_config)])

    project_dir = Path("dummy-project").resolve()
    os.chdir(str(project_dir))
    yield project_dir
    os.chdir(cwd_)


@pytest.fixture
def project_context(dummy_kedro_project) -> KedroContext:
    return load_context(".")
