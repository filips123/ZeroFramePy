"""ZeroFrame WebSocket API for Python."""

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=line-too-long

from asyncio import Future
import urllib.request
import threading
import time
import json
import sys
import re

import websocket


from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = '0.0.0'


CMD_RESPONSE = 'response'
CMD_PING = 'ping'
CMD_PONG = 'pong'


class ZeroFrame:
    """Class for ZeroFrame WebSocket API."""

    # Initialization & Connection

    def __init__(
            self,

            site,

            multiuser_master_address=None,
            multiuser_master_seed=None,

            instance_host='127.0.0.1',
            instance_port=43110,
            instance_secure=False,

            show_log=False,
            show_error=False,

            reconnect_attempts=-1,
            reconnect_delay=5000
    ):
        """
        Construct the class and set up a connection to the WebSocket server.

        :param str site: target ZeroNet site address

        :param str multiuser_master_address: master address for multiuser ZeroNet instance, defaults to `None`
        :param str multiuser_master_seed: master seed for multiuser ZeroNet instance, defaults to `None`

        :param str instance_host: host of ZeroNet instance, defaults to `127.0.0.1`
        :param int instance_port: port of ZeroNet instance, defaults to `43110`
        :param bool instance_secure: secure connection of ZeroNet instance, defaults to `False`

        :param bool show_log=false: show log messages in console, defaults to `False`
        :param bool show_error=false: show error messages in console, defaults to `False`

        :param int reconnect_attempts: number of attempts, defaults to `-1`, no limit with `-1`, no reconnect with `0`
        :param int reconnect_delay: number of delay in milliseconds, defaults to `5000`
        """

        self.site = site

        self.multiuser = {'master_address': multiuser_master_address, 'master_seed': multiuser_master_seed}
        self.instance = {'host': instance_host, 'port': instance_port, 'secure': instance_secure}
        self.show = {'log': show_log, 'error': show_error}
        self.reconnect = {'attempts': reconnect_attempts, 'delay': reconnect_delay}

        self.websocket_connected = False
        self.waiting_callbacks = {}
        self.waiting_messages = []
        self.next_message_id = 1
        self.next_attempt_id = 1

        self.wrapper_key = None
        self.websocket = None

        self._connect()
        self._start()


    def __getattr__(self, name):
        """
        Proxy for accessing ZeroFrame commands.

        Command name is accepted as an object's property and parameters are accepted as
        a method's arguments. Command returns `asyncio.Future` with the result.

        * Command with no arguments can be accessed with `zeroframe.cmdName()`.
        * Command with keyword arguments can be accessed with `zeroframe.cmdName(key1=value1, key2=value2)`.
        * Command with normal arguments can be accessed with `zeroframe.cmdName(value1, value2)`.
        """

        return lambda *args, **kwargs: self.cmdp(name, *args, **kwargs)

    def init(self):
        """
        User-based initialization code.

        :rtype: ZeroFrame
        """

        return self

    def _connect(self):
        """
        Get wrapper key and connect to WebSocket.

        :rtype: ZeroFrame
        """

        self.wrapper_key = self._get_wrapper_key()
        self.websocket = self._get_websocket()

        return self.init()

    def _start(self):
        """
        Start WebSocket in thread.
        """

        wst = threading.Thread(target=self.websocket.run_forever)
        wst.daemon = True
        wst.start()

    def _get_wrapper_key(self):
        """
        Get and return wrapper key.

        :return: wrapper key
        :rtype: str
        """

        site_url = 'http' + ('s' if self.instance['secure'] else '') + '://' + self.instance['host'] + ':' + str(self.instance['port']) + '/' + self.site

        wrapper_request = urllib.request.Request(site_url, headers={'Accept': 'text/html', 'User-Agent': 'ZeroFramePy/' + __version__})
        wrapper_body = urllib.request.urlopen(wrapper_request).read()

        wrapper_key = re.search(r'wrapper_key = "(.*?)"', str(wrapper_body)).group(1)
        return wrapper_key

    def _get_websocket(self):
        """
        Connect and return WebSocket.

        :return: WebSocket connection
        :rtype: object
        """

        ws_url = 'ws' + ('s' if self.instance['secure'] else '') + '://' + self.instance['host'] + ':' + str(self.instance['port']) + '/Websocket?wrapper_key=' + self.wrapper_key

        if not self.multiuser['master_address']:
            ws_client = websocket.WebSocketApp(ws_url)
        else:
            ws_client = websocket.WebSocketApp(ws_url, cookie='master_address=' + self.multiuser['master_address'])

        ws_client.on_message = self._on_request
        ws_client.on_open = self._on_open_websocket
        ws_client.on_error = self._on_error_websocket
        ws_client.on_close = self._on_close_websocket

        return ws_client

    # Internal handlers

    def _on_request(self, message):
        """
        Internal on request handler.

        It is triggered on every message from the WebSocket server.
        It handles built-in commands and forwards others
        to the user-based handler.

        :func:`~zeroframe_ws_client.ZeroFrame.on_request`

        :param str message: WebSocket message
        """

        message = json.loads(message)
        cmd = message['cmd']

        if cmd == CMD_RESPONSE:
            if message['to'] in self.waiting_callbacks:
                self.waiting_callbacks[message['to']](message['result'])
                del self.waiting_callbacks[message['to']]

        elif cmd == CMD_PING:
            self.response(message['id'], CMD_PONG)

        else:
            self.on_request(cmd, message)

    def _on_open_websocket(self):
        """
        Internal on open websocket handler.

        It is triggered when the WebSocket connection is opened.
        It sends waiting message and calls the user-based handler.

        :func:`~zeroframe_ws_client.ZeroFrame.on_open_websocket`
        """

        self.websocket_connected = True

        for message in self.waiting_messages:
            if not 'processed' in message:
                self.websocket.send(json.dumps(message))
                message['processed'] = True

        self.on_open_websocket()

    def _on_error_websocket(self, error):
        """
        Internal on error websocket handler.

        It is triggered on the WebSocket error. It calls the user-based client.

        :func:`~zeroframe_ws_client.ZeroFrame.on_error_websocket`

        :param object error: WebSocket exception
        """

        self.on_error_websocket(error)

    def _on_close_websocket(self):
        """
        Internal on close websocket handler.

        It is triggered when the WebSocket connection is closed.
        It tries to reconnect if enabled and calls the user-based handler.

        :func:`~zeroframe_ws_client.ZeroFrame.on_close_websocket`
        """

        self.websocket_connected = False

        self.on_close_websocket()

        if self.reconnect['attempts'] == 0:
            return

        if self.reconnect['attempts'] != -1 and self.next_attempt_id > self.reconnect['attempts']:
            return

        time.sleep(self.reconnect['delay'] / 1000)
        self.websocket = self._get_websocket()
        self._start()

    # External handlers

    def on_request(self, cmd, message): # pylint: disable=unused-argument
        """
        User-based on request handler.

        It is triggered on every message from the WebSocket server.
        It can be used to add additional functionalities to
        the client or handle received messages.

        :param str cmd: name of received command
        :param object message: message of received command
        """

        self.log('Unknown request', message)

    def on_open_websocket(self):
        """
        User-based on open websocket handler.

        It is triggered when the WebSocket connection is opened.
        It can be used to notify user or check for server details.
        """

        self.log('Websocket open')

    def on_error_websocket(self, error):
        """
        User-based on error websocket handler.

        It is triggered on the WebSocket error.
        It can be used to notify user or display errors.

        :param object error: WebSocket error
        """

        self.error('Websocket error', error)

    def on_close_websocket(self):
        """
        User-based on close websocket handler.

        It is triggered when the WebSocket connection is closed.
        It can be used to notify user or display connection error.
        """

        self.log('Websocket close')

    # Logging functions

    def log(self, *args):
        """
        Add log to console if enabled.

        :param * *args: logs to add to console
        """

        if self.show['log']:
            print('[ZeroFrame]', *args, file=sys.stdout)

    def error(self, *args):
        """
        Add error to console if enabled.

        :param * *args: errors to add to console
        """

        if self.show['error']:
            print('[ZeroFrame]', *args, file=sys.stderr)

    # Command functions

    def _send(self, message, cb=None): # pylint: disable=invalid-name
        """
        Internally send raw message to ZeroFrame server and call callback.

        If the connection is available, it directly sends a message. If the
        connection is not available, it adds message to waiting message queue.

        :func:`~zeroframe_ws_client.ZeroFrame.cmd`
        :func:`~zeroframe_ws_client.ZeroFrame.cmdp`
        :func:`~zeroframe_ws_client.ZeroFrame.response`

        :param dict message: message to send
        :param callable cb: message callback
        """

        if not 'id' in message:
            message['id'] = self.next_message_id
            self.next_message_id += 1

        if self.websocket_connected:
            self.websocket.send(json.dumps(message))
        else:
            self.waiting_messages.append(message)

        if cb:
            self.waiting_callbacks[message['id']] = cb

    def cmd(self, cmd, params=None, cb=None): # pylint: disable=invalid-name
        """
        Send command to ZeroFrame server and call callback.

        :param str cmd: name of command to send
        :param dict params: parameters of command to send
        :param callable cb: command callback
        """

        if not params:
            params = {}

        self._send({
            'cmd': cmd,
            'params': params
        }, cb)

    def cmdp(self, cmd, params=None):
        """
        Send command to ZeroFrame server and return the result as asyncio future.

        In most cases, the result will be dictionary which contains data.
        Some commands don't have any result. In this case, the result
        will probably be string `ok`.

        `ZeroFrame API Reference <https://zeronet.io/docs/site_development/zeroframe_api_reference/>`_

        :param str cmd: name of command to send
        :param dict params: parameters of command to send

        :return: command response
        :rtype: asyncio.Future<(dict|str)>
        """

        future = Future()
        self.cmd(cmd, params, future.set_result)

        return future

    def response(self, to, result): # pylint: disable=invalid-name
        """
        Response to ZeroFrame message.

        :param to cmd: message ID to response
        :param result cmd: result to send
        """

        self._send({
            'cmd': CMD_RESPONSE,
            'to': to,
            'result': result
        })
