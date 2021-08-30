import time
from unittest import TestCase
import socket
from threading import Thread

from pysockmmsg import recvmsg


class PktSender(Thread):
    def __init__(self, msg: bytes, port: int) -> None:
        """
        Builds a thread to send packets with the given message
        to the given port.
        """
        super(PktSender, self).__init__()
        self.port = port
        self.msg = msg
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.should_send = True

    def run(self) -> None:
        while self.should_send:
            self.sock.sendto(self.msg, ("localhost", self.port))
            time.sleep(0.1)

    def join(self, *args, **kwargs) -> None:
        self.should_send = False
        self.sock.close()
        super(PktSender, self).join(*args, **kwargs)


class TestRecvMsg(TestCase):
    def test_recvmsg(self):
        port = 5555
        sender = PktSender(b"some msg", port)
        sender.start()
        self.addCleanup(sender.join)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(sock.close)
        sock.bind(("localhost", port))
        data, addr = recvmsg(sock, 128)
        self.assertEqual(b"some msg", data)
        self.assertListEqual(list(addr.sin_addr), [127, 0, 0, 1])
