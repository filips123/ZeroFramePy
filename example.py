"""Example for ZeroFrame WebSocket API."""

import time

from zeroframe_ws_client import ZeroFrame


class ZeroApp(ZeroFrame):
    """Example for modified ZeroFrame class."""

    def on_request(self, cmd, message):
        """Example for handling custom ZeroFrame command."""

        if cmd == 'helloWorld':
            self.log('Hello World')


def main():
    """Handle example."""

    zeroapp = ZeroApp('1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D')

    result = zeroapp.cmdp('siteInfo')
    time.sleep(0.01)
    print(result.result())


main()
