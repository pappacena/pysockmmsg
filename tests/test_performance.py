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

        data_to_send = {
            (host, port): [b"a sent msg" for _ in range(total_packets)]
        }

        def send_using_sendmmsg():
            sendmmsg(sock, data_to_send, total_packets)

        def send_using_sendmsg():
            for dest, packets in data_to_send.items():
                for data in packets:
                    sendmsg(sock, dest, data)

        def send_using_raw_python():
            for dest, packets in data_to_send.items():
                for data in packets:
                    sock.sendto(data, dest)

        mmsg_time = timeit.timeit(send_using_sendmmsg, number=10)
        msg_time = timeit.timeit(send_using_sendmsg, number=10)
        raw_time = timeit.timeit(send_using_raw_python, number=10)
        print("Timers: ", mmsg_time, msg_time, raw_time)
        self.assertLess(mmsg_time, msg_time)
        self.assertLess(mmsg_time, raw_time)
