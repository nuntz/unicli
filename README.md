# unicli

A lightweight command light interface to the Ubiquiti Networks Unifi REST API (tested with version 5).

​	 For a more comprehensive interface, see [unifi-api](https://github.com/calmh/unifi-api).

## Installation

To install:

```shell
$ pip install --editable .
```

## Usage

Run:

```shell
$ unicli --help
```



## Examples

List all the clients:

```shell
$ unicli --host mycontroller --port 8443 --no-verify --user ubnt --site default list
```

Block a client:

```shell
$ unicli --host mycontroller --port 8443 --no-verify --user ubnt --site default block 01:23:45:67:89:ab
```

