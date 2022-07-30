import axel.services.net.data_structures as ds
import axel.services.net.server as serv
import socket
from functools import partial
from time import sleep
from string import ascii_letters, ascii_uppercase, ascii_lowercase


def test_packet_init():
    p = ds.Packet(1, 2, 3, 4)
    assert p.type == 1
    assert p.value == 2
    assert p.data == 3
    assert p.extra == 4
    assert len(p.storage) == 4


def test_packet_setters():
    p = ds.Packet()
    assert not any((p.type, p.value, p.data, p.extra))
    p.set_type("a")
    p.set_value("b")
    p.set_data("c")
    p.set_extra("d")
    assert all((p.type, p.value, p.data, p.extra))


def test_packet_comparison():
    a = ds.Packet(1, 2)
    b = ds.Packet(1, 2)
    assert a == b
    b.set_type(2)
    assert a != b


def test_packet_gen_and_parse():
    p = ds.Packet(1, 2, 3, 4)
    gen = p.generate()
    assert len(gen) > 10
    new = ds.Packet().parse(gen)
    assert new == p


def client_handle(message: bytes, conn: socket.socket, *args):
    conn.sendall(message)
    conn.close()


def test_wrapped_partial():
    """
    We can parse a single set packet
    """
    wrap = ds.WrappedConnection(None)  # None will not work with real sockets
    assert not wrap.partial  # Starts with nothing
    assert not wrap.finished
    wrap.partial = ds.Packet(1).generate()
    assert wrap.partial  # Something is queued up
    wrap.parse_partial()
    assert not wrap.partial  # Everything gets parsed and mooved
    assert wrap.finished
    assert wrap.finished[0] == ds.Packet(1)


def test_two_wrapped_partial():
    """
    We can send and parse multiple packets
    """
    wrap = ds.WrappedConnection(None)
    wrap.partial = ds.Packet(1).generate() + ds.Packet(2).generate()
    assert wrap.partial
    wrap.parse_partial()
    assert len(wrap.finished) == 2
    assert wrap.finished[1].type == 2


def test_partial_wrapped_partial():
    """
    Show we can parse all finished packets in the partial queue and leave incomplete ones
    """
    wrap = ds.WrappedConnection(None)
    p = ds.Packet(1)
    payload = p.generate() * 2
    cut = payload[:-5]
    wrap.partial = cut
    wrap.parse_partial()
    assert len(wrap.finished) == 1
    assert wrap.finished[0] == p
    assert wrap.partial == p.generate()[:-5]


def test_parse_sent_packet():
    port = serv.get_first_port_from(13131)
    p = ds.Packet(1, 2)
    s = serv.Server(port, partial(client_handle, p.generate()))

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(("localhost", port))  # connecting is a blocking only operation so it must be done first
    wrap = ds.WrappedConnection(conn)

    sleep(.01)  # Socket has some delay needed
    assert not wrap.partial
    wrap.load_awaited()
    assert wrap.partial
    wrap.parse_partial()
    assert not wrap.partial
    assert wrap.finished[-1] == p

    s.shutdown()


def test_gen_stream():
    base = ascii_letters.encode("utf-8")
    prep = ds.WrappedConnection.prep_stream(base)
    assert len(prep) >= len(base) + 2  # At least two field need to be inserted


def test_parse_stream():
    base = ascii_letters.encode("utf-8")
    wrap = ds.WrappedConnection(None)
    wrap.partial = wrap.prep_stream(base)

    wrap.parse_partial()
    assert len(wrap.finished) == 0  # Nothing should happen when the wrapper is in the wrong mode
    wrap.mode = "stream"
    wrap.parse_partial()
    assert len(wrap.finished) == 1
    assert wrap.finished[0] == ascii_letters.encode("utf-8")


def test_parse_other_stream():
    base = ascii_uppercase.encode("utf-8")
    other = ascii_lowercase.encode("utf-8")
    wrap = ds.WrappedConnection(None)
    wrap.mode = 'stream'
    wrap.partial = wrap.prep_stream(base) + wrap.prep_stream(other)

    # Parse multiple streams queue up
    assert not wrap.finished
    wrap.parse_partial()
    assert len(wrap.finished) == 2
    assert wrap.finished[0] == ascii_uppercase.encode("utf-8")
    assert not wrap.partial

    wrap.finished = []
    wrap.partial = wrap.prep_stream(base) + wrap.prep_stream(other)[:-10]

    # Parse only finished stream parts
    wrap.parse_partial()
    assert len(wrap.finished) == 1
    assert wrap.finished[0] == base
    assert wrap.partial





