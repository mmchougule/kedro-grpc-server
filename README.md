# Kedro gRPC Server

[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)]()
[![Current Version](https://img.shields.io/badge/current%20version-0.1-yellow.svg)]()
[![Python Version](https://img.shields.io/badge/python-3.6%20%7C%203.7-blue.svg)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

This is a beta Kedro plugin that creates a gRPC server for your kedro pipelines. Kedro gRPC Server RPC calls can be triggered using any of the programming languages that support gRPC.

Kedro gRPC clients can be in many programming languages.

Some kedro client examples below that call RPCs on a gRPC server running in any kedro project:
- [Python]()
- [Go]()
- [Scala]()
- [Java]()
- [Node]()
- C++
- C#
- Kotlin
- Dart

More on [grpc.io](https://grpc.io)

 - Code generation support in all gRPC frameworks makes it super easy to use for clients who may have a different tech stack and language preference. Simply sharing a kedro.proto file, clients can use their preferred programming language to generate strongly typed kedro clients in any of the languages mentioned above.
 - Allowing engineers to natively integrate running of kedro pipelines with their preferred programming language.
 - Getting status of kedro pipeline run as a streaming response through HTTP/2. gRPC provides first-class support for this.
 - Getting all the benefits of gRPC
 - And, enabling business users to interact with analytics from a front-end application and trigger actions or models (e.g. scoring  model) on demand.


## How do I install Kedro gRPC Server?

### Prerequisites

Kedro gRPC Server requires [Python 3.6+](https://realpython.com/installing-python/) and [Git](https://help.github.com/en/github/getting-started-with-github/set-up-git) to be setup.

#### Installation

You can install Kedro gRPC Server directly from GitHub with:

```bash
pip install git+https://github.com/mmchougule/kedro-grpc-server.git
```

## How do I use Kedro gRPC Server?

To start the server, simply run the following command inside your Kedro project:

```bash
kedro server grpc-start
```

You can specify the host through the flag like so:

```bash
kedro server grpc-start --host
```

Similarly, you can set the port number using `--port`.

## Run

## gRPC API

Exposing 3 RPC calls similar to the REST server:

`ListPipelines` -> Returns current list of pipelines

`Run` -> Runs a pipeline with or without arguments

`Status` -> Provides run status of a pipeline with run_id.
The response for this rpc call is a Server Streaming response of all logged events.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:
* The contribution code of conduct
* The process for submitting pull requests

## Versioning

We use [SemVer](http://semver.org/) for versioning. The best way to safely upgrade is to check our [release notes](RELEASE.md) for any notable breaking changes.

## What licence do you use?

See [LICENSE](LICENSE.md) for guidelines.
