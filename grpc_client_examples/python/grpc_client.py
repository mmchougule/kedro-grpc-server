import grpc

from kedro_grpc_server.kedro_pb2 import (  # type: ignore
    PipelineParams,
    RunId,
    RunParams,
)
from kedro_grpc_server.kedro_pb2_grpc import KedroStub  # type: ignore


# open a gRPC channel
def run_client(c):
    # create a stub (client)
    stub = KedroStub(c)

    # create a valid request message
    # number = calculator_pb2.Number(value=16)
    req = PipelineParams()

    # make the call
    # response = stub.SquareRoot(number)
    response = stub.ListPipelines(req)
    print(response.pipeline)

    run = RunParams(pipeline_name="de")

    run_response = stub.Run(run)

    print(run_response.run_id)

    run_req = RunId(run_id=run_response.run_id)

    res = stub.Status(run_req)

    for r in res:
        print(r.events)


if __name__ == '__main__':
    channel = grpc.insecure_channel("localhost:50051")

    run_client(channel)
