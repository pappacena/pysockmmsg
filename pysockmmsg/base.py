import os
import socket
from ctypes import (
    CDLL,
    POINTER,
    Structure,
    addressof,
    byref,
    c_byte,
    c_int,
    c_size_t,
    c_uint,
    c_uint8,
    c_uint32,
    c_ushort,
    c_void_p,
    cast,
    create_string_buffer,
    get_errno,
    pointer,
    sizeof,
)
from typing import List, Dict, Tuple

MSG_ERRQUEUE = 0x2000
MSG_WAITALL = 0x100
MSG_WAITFORONE = 0x10000


class struct_iovec(Structure):
    _fields_ = [
        ("iov_base", c_void_p),
        ("iov_len", c_size_t),
    ]


class struct_msghdr(Structure):
    _fields_ = [
        ("msg_name", c_void_p),
        ("msg_namelen", c_uint32),
        ("msg_iov", POINTER(struct_iovec)),
        ("msg_iovlen", c_size_t),
        ("msg_control", c_void_p),
        ("msg_controllen", c_size_t),
        ("msg_flags", c_int),
    ]


class struct_mmsghdr(Structure):
    _fields_ = [
        ("msg_hdr", struct_msghdr),
        ("msg_len", c_uint)
    ]

class struct_cmsghdr(Structure):
    _fields_ = [
        ("cmsg_len", c_size_t),
        ("cmsg_level", c_int),
        ("cmsg_type", c_int),
    ]


class struct_tpacket_auxdata(Structure):
    _fields_ = [
        ("tp_status", c_uint),
        ("tp_len", c_uint),
        ("tp_snaplen", c_uint),
        ("tp_mac", c_ushort),
        ("tp_net", c_ushort),
        ("tp_vlan_tci", c_ushort),
        ("tp_padding", c_ushort),
    ]


class sockaddr_in(Structure):
    _fields_ = [
        ("sa_family", c_ushort),
        ("sin_port", c_ushort),
        ("sin_addr", c_byte * 4),
        ("__pad", c_byte * 8),
    ]


class sockaddr_in6(Structure):
    _fields_ = [
        ("sin6_family", c_byte),
        ("sin6_port", c_ushort),
        ("sin6_flowinfo", c_uint32),
        ("sin6_addr", c_byte * 16),
        ("sin6_scope_id", c_uint32),
    ]


class sockaddr_storage(Structure):
    _fields_ = [
        ("sa_len", c_uint8),
        ("sa_family", c_uint8),
        ("sa_data", c_uint8 * 254),
    ]


class sock_extended_err(Structure):
    """
    {
        uint32_t ee_errno;   /* error number */
        uint8_t  ee_origin;  /* where the error originated */
        uint8_t  ee_type;    /* type */
        uint8_t  ee_code;    /* code */
        uint8_t  ee_pad;     /* padding */
        uint32_t ee_info;    /* additional information */
        uint32_t ee_data;    /* other data */
        /* More data may follow */
    };
    """

    _fields_ = [
        ("ee_errno", c_uint32),
        ("ee_origin", c_uint8),
        ("ee_type", c_uint8),
        ("ee_code", c_uint8),
        ("ee_pad", c_uint8),
        ("ee_info", c_uint32),
        ("ee_data", c_uint32),
    ]


libc = CDLL("libc.so.6")
_recvmsg = libc.recvmsg
_recvmsg.argtypes = [c_int, POINTER(struct_msghdr), c_int]
_recvmsg.restype = c_int

_sendmsg = libc.sendmsg
_sendmsg.argtypes = [c_int, POINTER(struct_msghdr), c_int]
_sendmsg.restype = c_int

_sendmmsg = libc.sendmmsg
_sendmmsg.argtypes = [c_int, POINTER(struct_mmsghdr), c_uint, c_int]
_sendmmsg.restype = c_int


def recvmsg(sock, bufsize):
    buf = create_string_buffer(bufsize)
    ctrl_bufsize = (
        sizeof(struct_cmsghdr) + sizeof(sock_extended_err) + sizeof(c_size_t)
    )

    ctrl_buf = create_string_buffer(ctrl_bufsize)

    iov = struct_iovec()
    iov.iov_base = cast(buf, c_void_p)
    iov.iov_len = bufsize

    addr = create_string_buffer(sizeof(sockaddr_storage))
    addr_len = c_uint(sizeof(addr))

    msghdr = struct_msghdr()
    msghdr.msg_name = addressof(addr)
    msghdr.msg_namelen = addr_len
    msghdr.msg_iov = pointer(iov)
    msghdr.msg_iovlen = 1
    msghdr.msg_control = cast(ctrl_buf, c_void_p)
    msghdr.msg_controllen = ctrl_bufsize
    msghdr.msg_flags = 0
    ret = _recvmsg(sock.fileno(), byref(msghdr), MSG_WAITFORONE)
    raise_if_socket_error(ret)
    data = buf.raw[:ret]

    addr = to_socket_addr(addr, msghdr.msg_namelen)
    return data, addr


def sendmsg(sock: socket.socket, destination: Tuple,
            data: bytes, flags: int = 0):
    """Sends a single message using the given socket."""
    # Convert the destination address into a struct sockaddr.
    to = sockaddr_from_tupe(destination)
    msg_namelen = sizeof(to)
    msg_name = cast(pointer(to), c_void_p)

    iov = struct_iovec(cast(data, c_void_p), len(data))  # type: ignore
    msg_iov = pointer(iov)
    msg_iovlen = 1

    msg_control = 0
    msg_controllen = 0

    msghdr = struct_msghdr(
        msg_name, msg_namelen, msg_iov, msg_iovlen,
        msg_control, msg_controllen, flags)

    ret = _sendmsg(sock.fileno(), msghdr, 0)
    raise_if_socket_error(ret)
    return ret


def sendmmsg(sock: socket.socket, data: Dict[Tuple, List],
             total_packets: int):
    """
    Send multiple messages at once.

    data should be a list of tuples in the format [(data, (host, port)), ...].
    total_packets should be provided for performance reason.
    """
    msghdr_len = total_packets
    m_msghdr = (struct_mmsghdr * msghdr_len)()

    i = 0
    for destination, packets in data.items():
        to = sockaddr_from_tupe(destination)
        msg_namelen = sizeof(to)
        msg_name = cast(pointer(to), c_void_p)
        msg_control = 0
        msg_controllen = 0
        msg_iovlen = 1
        for pkt in packets:
            iov = struct_iovec(cast(pkt, c_void_p), len(pkt))
            msg_iov = pointer(iov)

            msghdr = struct_msghdr(
                msg_name, msg_namelen, msg_iov, msg_iovlen,
                msg_control, msg_controllen, 0)

            m_msghdr[i] = struct_mmsghdr(msghdr)
            i += 1

    ret = _sendmmsg(sock.fileno(), m_msghdr[0], msghdr_len, 0)
    raise_if_socket_error(ret)
    return ret


def raise_if_socket_error(ret: int) -> None:
    """Checks socket functions return code and raise if it's an error code."""
    if ret < 0:
        errno = get_errno()
        raise socket.error(errno, os.strerror(errno))


def to_socket_addr(addr, addr_len):
    # Attempt to convert the address to something we understand.
    if addr_len == 0:
        return None
    if addr_len == sizeof(sockaddr_in):
        return sockaddr_in.from_buffer(addr)
    if addr_len == sizeof(sockaddr_in6):
        return sockaddr_in6.from_buffer(addr)
    return addr  # Unknown or malformed. Return the raw bytes.


def sockaddr_from_tupe(addr):
    """
    Converts a socket address tuple (host, port) to a proper socketaddr_* 
    C struct.

    @param addr:
    @return:
    """
    if ":" in addr[0]:
        family = socket.AF_INET6
        if len(addr) == 4:
            addr, port, flowinfo, scope_id = addr
        else:
            (addr, port), flowinfo, scope_id = addr, 0, 0
        addr = cast(socket.inet_pton(family, addr), POINTER(c_byte * 16))
        return sockaddr_in6(
            family, socket.ntohs(port), socket.ntohl(flowinfo),
            addr.contents, scope_id)
    else:
        family = socket.AF_INET
        addr, port = addr
        addr = cast(socket.inet_pton(family, addr), POINTER(c_byte * 4))
        return sockaddr_in(family, socket.ntohs(port), addr.contents)
