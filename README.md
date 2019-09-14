ZeroFramePy
===========

[![version][icon-version]][link-pypi]
[![downloads][icon-downloads]][link-pypi]
[![license][icon-license]][link-license]
[![python][icon-python]][link-python]
[![build][icon-travis]][link-travis]

ZeroFrame WebSocket API for Python.

## Description

This is Python WebSocket client for [ZeroFrame API][link-zeroframe]. It supports (almost) same features as default ZeroFrame that is included in ZeroNet sites, but it is using WebSocket client so it can be used in local programs.

## Installation

### Requirements

ContentHash requires Python 3.5 or higher.

### From PyPI

The recommended way to install ContentHash is from PyPI with PIP.

```bash
pip install zeroframe-ws-client
```

### From Source

Alternatively, you can also install it from the source.

```bash
git clone https://github.com/filips123/ZeroFramePy.git
cd ZeroFramePy
python setup.py install
```

## Usage

### Importing Package

You can import ZeroFrameJS from `zeroframe_ws_client` package.

```py
from zeroframe_ws_client import ZeroFrame
```

### Creating Connection

To create a connection, you need to specify the ZeroNet site address.

```py
zeroframe = ZeroFrame('1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D')
```

If ZeroNet instance is using `Multiuser` plugin, you need to specify a master address of the account you want to use. Account must already exist on the instance.

```py
zeroframe = ZeroFrame(
    '1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D',
    multiuser_master_address='1Hxki73XprDRedUdA3Remm3kBX5FZxhFR3'
)
```

If you want to create a new account, you also need to specify a master seed of it. Note that this feature is unsafe on the untrusted proxy. Also, it is currently not implemented yet.

```py
zeroframe = ZeroFrame(
    '1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D',
    multiuser_master_address='1KAtuzxwbD1QuMHMuXWcUdoo5ppc5wnot9',
    multiuser_master_seed='fdbaf75427ba69a3d4aa8e19372e05879e9e2d866e579dd30be25e6fab7e3fb2'
)
```

If needed, you can also specify protocol, host and port of ZeroNet instance.

```py
zeroframe = ZeroFrame(
    '1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D',
    instance_host='192.168.1.1',
    instance_port=8080,
    instance_secure=True
)
```

Log and error message from `zeroframe.log` and `zeroframe.error` will not be displayed by default. If you want to, you can also display them as debug info.

```py
zeroframe = ZeroFrame(
    '1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D',
    show_log=True,
    show_error=True
)
```

By default, the client will try to reconnect WebSocket if the connection was closed every 5 seconds. You can also configure time delay and total attempts. Delay is specified in milliseconds. The number of attempts `-1` means infinity and `0` means zero (disabled reconnecting).

```py
zeroframe = ZeroFrame(
    '1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D',
    reconnect_attempts=10,
    reconnect_delay=1000
)
```

The client will then obtain wrapper key to the site and connect to WebSocket using it.

You can now normally use ZeroFrame API. Just remember that there is no wrapper, so wrapper commands are not available. The client is connected directly to the WebSocket server, so you need to use its commands.

Note that the WebSocket server sometimes sends commands (`notification`, `progress`, `error`, `prompt`, `confirm`, `setSiteInfo`, `setAnnouncerInfo`, `updating`, `redirect`, `injectHtml`, `injectScript`) that are normally handled by the wrapper. Because there is no wrapper, you need to handle those commands yourself if needed. Commands `response` and `ping` are already handled by this client so you don't need to handle them.

### Sending Command

You can use the `cmd` method to issue commands.

```py
zeroframe.cmd(
  'siteInfo',
  {},
  lambda result: print(result)
)
```

You can also use the `cmdp` method to get results as Python asyncio futures.

```py
result = zeroframe.cmd('siteInfo', {})
print(result.result())
```

### Sending Response

To submit responses, you need to use `response` command.

```py
zeroframe.response(10, 'Hello World')
```

### Logging Information

There are also `log` and `error` methods which are available for logging. They will display output to console if enabled.

```py
zeroframe.log('Connected')
zeroframe.error('Connection failed')
```

### Handling Connection

There are also public handler methods which you can overwrite to add your own logic to ZeroFrame.

```py
class ZeroApp(ZeroFrame):
    def on_request(self, cmd, message):
        if cmd == 'helloWorld':
            self.log('Hello World')

    def on_open_websocket(self):
        self.log('Connected to WebSocket')

    def on_error_websocket(self, error):
        self.error('WebSocket connection error')

    def on_close_websocket(self):
        self.error('WebSocket connection closed')
```

### Calling Commands Directly

You can also directly call commands via `__getattr__` method. Command name is accepted as an object's property and parameters are accepted as a method's arguments. Command returns `asyncio.Future` with the result.

 * Command with no arguments can be accessed with `zeroframe.cmdName()`.
 * Command with keyword arguments can be accessed with `zeroframe.cmdName(key1=value1, key2=value2)`.
 * Command with normal arguments can be accessed with `zeroframe.cmdName(value1, value2)`.

```py
siteInfo = zeroframe.siteInfo()
print(siteInfo.result())
```

### Other Examples

You could also look to [`example.py`][link-example].

## Versioning

This library uses [SemVer][link-semver] for versioning. For the versions available, see [the tags][link-tags] on this repository.

## License

This library is licensed under the MIT license. See the [LICENSE][link-license-file] file for details.

[icon-version]: https://img.shields.io/pypi/v/zeroframe-ws-client.svg?style=flat-square&label=version
[icon-downloads]: https://img.shields.io/pypi/dm/zeroframe-ws-client.svg?style=flat-square&label=downloads
[icon-license]: https://img.shields.io/pypi/l/zeroframe-ws-client.svg?style=flat-square&label=license
[icon-python]: https://img.shields.io/pypi/pyversions/zeroframe-ws-client.svg?style=flat-square&label=python
[icon-travis]: https://img.shields.io/travis/com/filips123/ZeroFramePy.svg?style=flat-square&labelbuild

[link-pypi]: https://pypi.org/project/zeroframe-ws-client/
[link-license]: https://choosealicense.com/licenses/mit/
[link-python]: https://python.org/
[link-travis]: https://travis-ci.com/filips123/ZeroFramePy/
[link-semver]: https://semver.org/

[link-tags]: https://github.com/filips123/ZeroFramePy/tags/
[link-license-file]: https://github.com/filips123/ZeroFramePy/blob/master/LICENSE
[link-example]: https://github.com/filips123/ZeroFramePy/blob/master/example.py

[link-zeroframe]: https://zeronet.io/
