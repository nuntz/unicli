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



## Supported Commands

Currently supported commands:

* `block`: block a client using its MAC address.
* `clients`: list active clients.
* `devices`: list devices (AP).
* `events`: display recent events.
* `reconnect`: reconnect a client using its MAC address.
* `unblock`: unblock a client using its MAC address.

## Examples

List all the clients:

```shell
$ unicli --host mycontroller --port 8443 --no-verify --user ubnt --site default list
```

Block a client:

```shell
$ unicli --host mycontroller --port 8443 --no-verify --user ubnt --site default block 01:23:45:67:89:ab
```

Hint: the password can also be accepted from an environment variable. To prevent the password from being stored in your history file, set the `HISTCONTROL` environment variable to *ignorespace* and prefix the export statement a blank space when setting the password:

```shell
$ export HISTCONTROL=ignorespace
$  export PASSWORD=foo
```

