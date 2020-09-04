"""Kedro run manager implementation: ProcessManager"""
import abc
import sys
import uuid
from functools import wraps
from multiprocessing import Process, Queue
from queue import Empty
from typing import Any, AnyStr, Callable, Dict, List, Union


def _get_new_events(events_queue: Queue):
    while True:
        try:
            yield events_queue.get_nowait()
        except Empty:
            break


def _wrapped_write(
    queue: Queue, real_write: Callable[[AnyStr], int]
) -> Callable[[AnyStr], int]:
    """Forward messages sent to `real_write` to a multiprocessing queue.

    Args:
        queue: Multiprocessing queue to forward the messages to.
        real_write: Write callable the message was addressed to. It's signature
            must be identical to `sys.stdout.write`.

    Returns:
        Wrapped write function.
    """

    # the signature of `_wrapped` is deliberately kept as close
    # to sys.stdout.write as possible
    @wraps(real_write)
    def _wrapped(s: AnyStr) -> int:  # pylint: disable=invalid-name
        s_to_queue = s.decode("utf-8") if isinstance(s, bytes) else s  # type: ignore
        if s_to_queue.strip():
            queue.put(s_to_queue)
        real_write(s)
        return len(s)

    return _wrapped


class AbstractManager(abc.ABC):
    """`AbstractManager` is the base class for all pipeline run managers
    """

    def __init__(
        self,
        context: Any,
        run_id: str = None,
        run_args: dict = None,
        extra_params: dict = None,
    ):
        """
        Instantiates the run manager class
        :param context: Project context
        :param run_id: Specific Run ID
        :param run_args: Run args
        :param extra_params: Extra params
        """
        self._context = context
        self._run_id = run_id or str(uuid.uuid4())
        self._run_args = run_args
        self._extra_params = extra_params or {}
        self._events = []  # type: List[str]
        self._run_finished = False

    @property
    def run_id(self):
        """Run_ID getter"""
        return self._run_id

    @property
    def events(self):
        """Events getter"""
        return self._events

    @abc.abstractmethod
    def start(self):
        """The abstract interface for starting run managers"""
        raise NotImplementedError(
            "`{}` is a subclass of AbstractManager and"
            "it must implement the `start` method".format(self.__class__.__name__)
        )

    @abc.abstractmethod
    def stop(self):
        """The abstract interface for stopping run managers"""
        raise NotImplementedError(
            "`{}` is a subclass of AbstractManager and"
            "it must implement the `stop` method".format(self.__class__.__name__)
        )

    @abc.abstractmethod
    def status(self):
        """The abstract interface for getting status of runs"""
        raise NotImplementedError(
            "`{}` is a subclass of AbstractManager and"
            "it must implement the `status` method".format(self.__class__.__name__)
        )


class ProcessManager(AbstractManager):
    """ProcessManager is an AbstractManager implementation.
    Uses multiprocessing Process to manage kedro runs"""

    def __init__(
        self,
        context,
        run_id=None,
        proc=None,
        queue=None,
        run_args=None,
        extra_params=None,
    ):
        """
        Instantiates the run manager class
        """
        super().__init__(
            context=context,
            run_id=run_id,
            run_args=run_args,
            extra_params=extra_params,
        )
        self._proc = proc or None
        self._proc_queue = queue or Queue()  # type: Queue

    @property
    def proc(self) -> Process:
        """Process getter"""
        return self._proc

    @property
    def proc_queue(self):
        """Process queue getter"""
        return self._proc_queue

    def start(self):
        """
        Start run process with queue
        """
        self._proc = Process(target=self._wrapped_run, daemon=True)
        self._proc.start()

    def stop(self) -> str:
        """
        Stop current process
        :return: Stop message
        """
        raise NotImplementedError("Run stop is not supported yet.")

    def status(self) -> Dict[Any, Union[str, list]]:
        """
        Return status of the current process
        :return:
        """

        new_events = _get_new_events(self._proc_queue)
        self.events.extend(new_events)
        return dict(
            run_status="Pending" if self.proc.is_alive() else "Completed",
            events=self._events,
        )

    def _wrapped_run(self):
        """Enhanced pipeline run to collect events"""
        sys.stdout.write = _wrapped_write(self._proc_queue, sys.stdout.write)
        sys.stderr.write = _wrapped_write(self._proc_queue, sys.stderr.write)

        self._proc_queue.put("Starting run")
        self._context.run(**self._run_args)
        self._proc_queue.put("Completed run")
