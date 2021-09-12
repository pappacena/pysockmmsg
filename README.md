# pysockmmsg

[![codecov](https://codecov.io/gh/pappacena/pysockmmsg/branch/main/graph/badge.svg?token=pysockmmsg_token_here)](https://codecov.io/gh/pappacena/pysockmmsg)
[![CI](https://github.com/pappacena/pysockmmsg/actions/workflows/main.yml/badge.svg)](https://github.com/pappacena/pysockmmsg/actions/workflows/main.yml)

Python wrappers for Linux's `sendmmsg` and `recvmmsg` system calls.

When sending/receiving a large amount of packets, preparing the data to be 
send/received using only a single system call can improve a lot the overal 
performance by reducing kernel/userland context switching.

## Install it from PyPI

```bash
pip install pysockmmsg
```

## Usage

### Sending multiple messages at a time
```py
import socket
from pysockmmsg import sendmmsg

data_to_send = {
    ('10.10.1.20', '5555'): [b"msg1", b"msg2", b"msg3"],
    ('10.10.1.25', '5555'): [b"msg4", b"msg5"],
    ('10.10.1.26', '5555'): [b"msg6", b"msg7", b"msg8", b"msg9"],
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sendmmsg(sock, data_to_send, total_packets=9)
```

## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
