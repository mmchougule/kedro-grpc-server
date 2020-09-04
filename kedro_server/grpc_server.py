"""Kedro gRPC Server"""
import logging
import time
from concurrent import futures
from copy import deepcopy
from typing import Any

import grpc
from kedro.framework.cli import get_project_context

from kedro_server.kedro_pb2 import (  # type: ignore
    PipelineSummary,
    RunStatus,
    RunSummary,
)
from kedro_server.kedro_pb2_grpc import (  # type: ignore
    KedroServicer,
    add_KedroServicer_to_server,
)
from kedro_server.process_manager import ProcessManager

# from kedro_server.utils import _get_new_events, start_run_process

RUN_STATES = {}


class KedroServer(KedroServicer):
    """
    KedroServer is an implementation of KedroServicer
    """

    def __init__(self, context):
        self.app_context = context

    def ListPipelines(self, request, context):
        response = PipelineSummary()
        pipeline_names = self.app_context.pipelines.keys()
        response.pipeline.extend(pipeline_names)  # pylint: disable=no-member
        return response

    def Run(self, request, context):
        run_args = dict(pipeline_name=request.pipeline_name, tags=request.tags,)

        context = deepcopy(self.app_context)
        # run_id, run_states = start_run_process(
        #     context=context, run_args=run_args, extra_params={}
        # )
        #
        # RUN_STATES[run_id] = run_states
        proc_manager = ProcessManager(
            context=context, run_args=run_args, extra_params={}
        )
        run_id = proc_manager.run_id
        proc_manager.start()

        RUN_STATES[run_id] = proc_manager

        response = RunSummary()
        response.run_id = run_id
        response.success = f"Run {run_id} dispatched"
        return response

    def Status(self, request, context):
        """Get run status and logged events"""
        run_id = request.run_id
        response = RunStatus()

        if run_id not in RUN_STATES:
            response.events.extend([])  # pylint: disable=no-member
            response.run_status = "Error"
            response.exit_code = ""
            response.success = "Run ID doesn't exist"
            response.run_id = run_id
            yield response
        else:
            has_events = True

            process_info = RUN_STATES[run_id]  # type: ProcessManager

            while has_events:
                proc_status = process_info.status()
                run_status = proc_status.get("run_status")
                response.run_id = run_id
                response.events.extend(  # pylint: disable=no-member
                    proc_status.get("events")
                )
                response.success = "Status check was performed successfully"
                response.run_status = run_status
                response.exit_code = str(process_info.proc.exitcode)

                yield response
                has_events = bool(process_info.proc.is_alive())
                time.sleep(1)


class KedroGrpcServerException(Exception):
    """
    Raise an Kedro gRPC Server exception
    :raises Exception
    """

    pass


def grpc_serve(
    context: Any = None,
    host: str = "[::]",
    port: int = 50051,
    max_workers: int = 10,
    wait_term: bool = True,
):
    """
    Start the Kedro gRPC server

    :param context: Kedro Project Context
    :param host: host for running the grpc server
    :param port: Port to run the gRPC server on
    :param max_workers: Max number of workers
    :param wait_term: Wait for termination

    :raises KedroGrpcServerException: Failing to start gRPC Server
    """
    try:
        if not context:
            context = get_project_context()
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        add_KedroServicer_to_server(KedroServer(context), server)
        server.add_insecure_port(f"{host}:{port}")
        server.start()
        logging.info("Kedro gRPC Server started on %s", port)
        if wait_term:  # pragma: no cover
            server.wait_for_termination()
    except Exception as exc:
        logging.error(exc)
        raise KedroGrpcServerException("Failed to start Kedro gRPC Server")
