"""This is a Kedro plugin that creates a gRPC server for your kedro pipelines."""

from typing import Dict

import click

from kedro_grpc_server.grpc_server import grpc_serve
from kedro_grpc_server.process_manager import ProcessManager

HOST_HELP = """Host which the server will listen to. Defaults to 127.0.0.1."""
PORT_HELP = """TCP port which the server will listen to. Defaults to 4141."""
MAX_WORKERS_HELP = """Number of ThreadExecutors to handle RPCs."""

RUN_STATES = {}  # type: Dict[str, ProcessManager]


@click.group(name="Server")
def commands():
    """Kedro plugin for gRPC Server"""


@commands.group(name="server")
def server_commands():
    """Run project with Kedro-gRPC-Server"""


@server_commands.command()
@click.option("--host", default="127.0.0.1", help=HOST_HELP)
@click.option("--port", default=50051, type=int, help=PORT_HELP)
@click.option("--max_workers", default=10, type=int, help=MAX_WORKERS_HELP)
def grpc_start(host, port, max_workers, wait_term=True):
    """Start Kedro gRPC Server"""
    grpc_serve(
        host=host, port=port, max_workers=max_workers, wait_term=wait_term
    )  # pragma: no cover
