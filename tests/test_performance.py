import socket
import timeit
from unittest import TestCase

from pysockmmsg import sendmsg
from pysockmmsg.base import sendmmsg


class TestSendMultipleMessages(TestCase):
    """These are time """
    def test_sendmmsg_vs_sendmsg(self):
        host = "127.0.0.1"
        port = 5555
        total_packets = 10_000
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(sock.close)

        data_to_send = [
            (b"a sent msg", (host, port))
            for _ in range(total_packets)
        ]

        def send_using_sendmmsg():
            sendmmsg(sock, data_to_send)

        def send_using_sendmsg():
            for data, dest in data_to_send:
                sendmsg(sock, dest, data)

        def send_using_raw_python():
            for data, dest in data_to_send:
                sock.sendto(data, dest)

        mmsg_time = timeit.timeit(send_using_sendmmsg, number=10)
        msg_time = timeit.timeit(send_using_sendmsg, number=10)
        raw_time = timeit.timeit(send_using_raw_python, number=10)
        print("Timers: ", mmsg_time, msg_time, raw_time)
        self.assertLess(mmsg_time, msg_time)
        self.assertLess(mmsg_time, raw_time)
