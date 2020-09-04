import re
from os import path

from setuptools import find_packages, setup

name = "kedro_grpc_server"
here = path.abspath(path.dirname(__file__))

# get package version
with open(path.join(here, name, "__init__.py"), encoding="utf-8") as f:
    result = re.search(r'__version__ = ["\']([^"\']+)', f.read())
    if not result:
        raise ValueError("Can't find the version in kedro_grpc_server/__init__.py")
    version = result.group(1)

# get the dependencies and installs
with open("requirements.txt", "r", encoding="utf-8") as f:
    requires = [x.strip() for x in f if x.strip()]

# get test dependencies and installs
with open("test_requirements.txt", "r", encoding="utf-8") as f:
    test_requires = [x.strip() for x in f if x.strip() and not x.startswith("-r")]

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    readme = f.read()

setup(
    name=name,
    version=version,
    description="Kedro gRPC Server, a Kedro plugin that creates a gRPC server for your kedro pipelines",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/mmchougule/kedro-grpc-server",
    author="Mayur Chougule",
    packages=find_packages(),
    python_requires=">=3.6, <3.8",
    include_package_data=True,
    tests_require=test_requires,
    install_requires=requires,
    zip_safe=False,
    entry_points={
        "kedro.project_commands": ["kedro_grpc_server = kedro_grpc_server.app:commands"]
    },
)
