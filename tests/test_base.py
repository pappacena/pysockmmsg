import time
from unittest import TestCase
import socket
from threading import Thread

from pysockmmsg import recvmsg


class PktSender(Thread):
    def __init__(self, msg: bytes, host: str, port: int, ipv: int=4) -> None:
        """
        Builds a thread to send packets with the given message
        to the given port.
        """
        super(PktSender, self).__init__()
        self.host = host
        self.port = port
        self.msg = msg
        opt = socket.AF_INET if ipv == 4 else socket.AF_INET6
        self.sock = socket.socket(opt, socket.SOCK_DGRAM)
        self.should_send = True

    def run(self) -> None:
        while self.should_send:
            self.sock.sendto(self.msg, (self.host, self.port))
            time.sleep(0.1)

    def join(self, *args, **kwargs) -> None:
        self.should_send = False
        self.sock.close()
        super(PktSender, self).join(*args, **kwargs)


class TestRecvMsg(TestCase):
    def test_recvmsg_ipv4(self):
        host = "127.0.0.1"
        port = 5555
        sender = PktSender(b"some msg", host, port)
        sender.start()
        self.addCleanup(sender.join)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(sock.close)
        sock.bind((host, port))
        data, addr = recvmsg(sock, 128)
        self.assertEqual(b"some msg", data)
        self.assertListEqual(list(addr.sin_addr), [127, 0, 0, 1])

    def test_recvmsg_ipv6(self):
        port = 5555
        host = "::1"
        sender = PktSender(b"some msg", host, port, 6)
        sender.start()
        self.addCleanup(sender.join)

        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.addCleanup(sock.close)
        sock.bind((host, port))
        data, addr = recvmsg(sock, 128)
        self.assertEqual(b"some msg", data)
        self.assertListEqual(
            list(addr.sin6_addr),
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
