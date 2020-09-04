import logging
import os
import signal
import sys
import time
from multiprocessing import Lock, Value
from typing import Dict

import grpc
import pytest
from kedro import __version__
from kedro.context import KedroContext
from kedro.io import DataCatalog
from kedro.pipeline import Pipeline, node
from kedro.versioning import Journal

# from kedro_server import process_manager
from kedro_server import process_manager
from kedro_server.grpc_server import (  # type: ignore
    RUN_STATES,
    KedroGrpcServerException,
    KedroServer,
    grpc_serve,
)
from kedro_server.kedro_pb2 import RunId, RunParams  # type: ignore
from kedro_server.kedro_pb2_grpc import add_KedroServicer_to_server  # type: ignore
from kedro_server.process_manager import ProcessManager

_lock = Lock()  # pylint: disable=invalid-name
_num_active_runs = Value("i", 0)


def dummy_node():  # pragma: no cover
    return "X"


def bad_node():  # pragma: no cover
    raise ValueError("Oh no!!!")


def printing_node():  # pragma: no cover
    print("Printed from printing_node")
    with _lock:
        logging.info("Logged from printing_node")
        logging.error("Error from printing_node")
        return "X"


#
#
# @pytest.fixture
# def fake_run_id(mocker):
#     mocker.patch("kedro_server.utils._generate_run_id", return_value="abc123")


@pytest.fixture
def fake_run_id(mocker):
    def get_proc_manager():  # pylint: disable=unused-argument
        return ProcessManager(context=None, run_id="abc123")

    mocker.patch(
        "kedro_server.process_manager.ProcessManager.run_id",
        new=get_proc_manager().run_id,
    )


@pytest.fixture(autouse=True)
def clear_stdout_stderr_monkeypatch():
    stdout_write = sys.stdout.write
    stderr_write = sys.stderr.write
    yield
    # clear all monkeypatches after the test
    sys.stdout.write = stdout_write
    sys.stderr.write = stderr_write


class DummyContext(KedroContext):
    project_name = "test"
    project_version = __version__

    def _setup_logging(self) -> None:
        pass

    def _get_pipelines(self) -> Dict[str, Pipeline]:
        return {
            "__default__": Pipeline([node(dummy_node, None, "y")]),
            "my_pipeline": Pipeline([node(dummy_node, None, "y")]),
            "error_pipeline": Pipeline([node(bad_node, None, "empty")]),
            "printing_pipeline": Pipeline([node(printing_node, None, "y")]),
        }

    def _get_catalog(
        self,
        save_version: str = None,
        journal: Journal = None,
        load_versions: Dict[str, str] = None,
    ) -> DataCatalog:
        return DataCatalog()  # pragma: no cover

    def run(self, *args, **kwargs):  # pylint: disable=arguments-differ
        with _num_active_runs.get_lock():
            _num_active_runs.value += 1
        try:
            return super().run(*args, **kwargs)
        finally:
            with _num_active_runs.get_lock():
                _num_active_runs.value -= 1


@pytest.fixture(scope="module")
def grpc_add_to_server():
    return add_KedroServicer_to_server


@pytest.fixture(scope="module")
def grpc_servicer(tmpdir_factory):
    dummy_context = DummyContext(str(tmpdir_factory))

    return KedroServer(dummy_context)


@pytest.fixture(scope="module")
def grpc_stub(grpc_channel):
    from kedro_server.kedro_pb2_grpc import KedroStub

    return KedroStub(grpc_channel)


def grpc_server_on(channel, timeout=2) -> bool:
    try:
        grpc.channel_ready_future(channel).result(timeout=timeout)
        return True
    except grpc.FutureTimeoutError:
        return False


def test_grpc_server_on(grpc_channel):
    assert grpc_server_on(grpc_channel, 2)


def test_grpc_server_on_timeout():
    ch = grpc.insecure_channel("localhost:8081")

    assert not grpc_server_on(ch, 1)


def test_grpc_serve(tmpdir_factory):
    dummy_context = DummyContext(str(tmpdir_factory))
    grpc_serve(dummy_context, wait_term=False)

    ch = grpc.insecure_channel("localhost:50051")

    assert grpc_server_on(ch)


def test_grpc_serve_no_context(tmpdir_factory):
    with pytest.raises(KedroGrpcServerException) as exc:
        grpc_serve(wait_term=False)

    assert "Failed to start" in str(exc.value)


def test_get_pipelines(grpc_stub):
    from kedro_server.kedro_pb2 import PipelineParams

    request = PipelineParams()
    response = grpc_stub.ListPipelines(request)
    assert response.pipeline == [
        "__default__",
        "my_pipeline",
        "error_pipeline",
        "printing_pipeline",
    ]


@pytest.mark.usefixtures("fake_run_id")
def test_run_success(grpc_stub):
    expected = {"success": "Run abc123 dispatched", "run_id": "abc123"}
    request = RunParams()
    response = grpc_stub.Run(request)

    assert response.success == expected["success"]
    assert response.run_id == expected["run_id"]

    process = RUN_STATES[response.run_id].proc

    os.kill(process.pid, signal.SIGTERM)
    for _ in range(10):
        time.sleep(1)
        if not process.is_alive():
            print("alive")
            break
    else:
        process.terminate()  # pragma: no cover

    # clean-up
    process.join()


def test_get_status(grpc_stub):
    """Test to check that events logged or printed end up in
    the events queue and returned in the response, along with
    the correct run_status.
    """
    with _lock:
        request = RunParams()
        run_response = grpc_stub.Run(request)
        run_id = run_response.run_id

        status_request = RunId(run_id=run_id)
        status_response = grpc_stub.Status(status_request)

        for status in status_response:
            assert status.run_id == run_id
            assert status.run_status != ""

    RUN_STATES[run_id].proc.join(3)  # join the process to make sure it finished
    status_request = RunId(run_id=run_id)
    status_response = grpc_stub.Status(status_request)
    run_status = None
    events = []
    for status in status_response:
        run_status = status.run_status
        events = status.events
    assert run_status == "Completed"
    assert any("Completed run" in ev for ev in events)


def test_get_status_wrong_run_id(grpc_stub):
    status_request = RunId(run_id="invalid")
    status_response = grpc_stub.Status(status_request)
    for status in status_response:
        assert status.run_id == "invalid"
        assert status.success == "Run ID doesn't exist"
        assert status.run_status == "Error"


def test_wrapped_run(mocker, capsys):
    # need to assign both to variables as will be wrapped by '_wrapped_write' later
    stdout_write = sys.stdout.write
    stderr_write = sys.stderr.write
    # from kedro_server import process_manager

    def _fake_run(**kwargs):
        print("Fake stdout")
        print(f"Running: {kwargs}")
        print("Fake stderr", file=sys.stderr)

    mock_wrapped_write = mocker.spy(process_manager, "_wrapped_write")
    queue = mocker.Mock()
    context = mocker.Mock()
    context.run.side_effect = _fake_run

    fake_run_args = {"some_arg": "some_value"}
    proc_manager = ProcessManager(context=context, queue=queue, run_args=fake_run_args)
    proc_manager._wrapped_run()

    assert mock_wrapped_write.mock_calls == [
        mocker.call(proc_manager.proc_queue, stdout_write),  # patch of sys.stdout.write
        mocker.call(proc_manager.proc_queue, stderr_write),  # patch of sys.stderr.write
    ]

    assert queue.put.mock_calls == [
        mocker.call("Starting run"),
        mocker.call("Fake stdout"),
        mocker.call(f"Running: {fake_run_args}"),
        mocker.call("Fake stderr"),
        mocker.call("Completed run"),
    ]
    context.run.assert_called_once_with(**fake_run_args)

    captured = capsys.readouterr()  # capture what was sent to sys.stdout/stderr
    assert captured.out == f"Fake stdout\nRunning: {fake_run_args}\n"
    assert captured.err == "Fake stderr\n"
