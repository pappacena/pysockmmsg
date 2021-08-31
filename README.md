# pysockmmsg

[![codecov](https://codecov.io/gh/pappacena/pysockmmsg/branch/main/graph/badge.svg?token=pysockmmsg_token_here)](https://codecov.io/gh/pappacena/pysockmmsg)
[![CI](https://github.com/pappacena/pysockmmsg/actions/workflows/main.yml/badge.svg)](https://github.com/pappacena/pysockmmsg/actions/workflows/main.yml)

Python wrappers for Linux's `sendmmsg` and `recvmmsg` system calls.

## Install it from PyPI

```bash
pip install pysockmmsg
```

## Usage

```py
from pysockmmsg import BaseClass
from pysockmmsg import base_function

BaseClass().base_method()
base_function()
```

```bash
$ python -m pysockmmsg
#or
$ pysockmmsg
```

## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
