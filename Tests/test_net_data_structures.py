import axel.services.net.data_structures as ds
import axel.services.net.server as serv
import socket
from functools import partial
from time import sleep
from string import ascii_letters, ascii_uppercase, ascii_lowercase


def test_packet_init():
    """
    Test Packet init
    """
    p = ds.Packet(1, 2, 3, 4)
    assert p.type == 1
    assert p.value == 2
    assert p.data == 3
    assert p.extra == 4
    assert len(p.storage) == 4


def test_packet_setters():
    """
    Test setters
    """
    p = ds.Packet()
    assert not any((p.type, p.value, p.data, p.extra))
    p.set_type("a")
    p.set_value("b")
    p.set_data("c")
    p.set_extra("d")
    assert all((p.type, p.value, p.data, p.extra))


def test_packet_comparison():
    """
    Test __eq__
    """
    a = ds.Packet(1, 2)
    b = ds.Packet(1, 2)
    assert a == b
    b.set_type(2)
    assert a != b


def test_packet_gen_and_parse():
    """
    Test byte generation and parsing
    """
    p = ds.Packet(1, 2, 3, 4)
    gen = p.generate()
    assert len(gen) > 10
    new = ds.Packet().parse(gen)
    assert new == p


def client_handle(message: bytes, conn: socket.socket, *args):
    # This is a helper function for the server

    conn.sendall(message)
    conn.close()


def test_wrapped_partial():
    """
    We can parse a single set packet
    """
    wrap = ds.WrappedConnection(None)  # None will not work with real sockets
    assert not wrap._partial  # Starts with nothing
    assert not wrap.finished
    wrap._partial = wrap._generate_final_obj(ds.Packet(1))
    assert wrap._partial  # Something is queued up
    wrap.parse_full_partial()
    assert not wrap._partial  # Everything gets parsed and mooved
    assert wrap.finished
    assert wrap.finished[0] == ds.Packet(1)


def test_two_wrapped_partial():
    """
    We can send and parse multiple packets
    """
    wrap = ds.WrappedConnection(None)
    wrap._partial = wrap._generate_final_obj(ds.Packet(1)) + wrap._generate_final_obj(ds.Packet(2))
    assert wrap._partial
    wrap.parse_full_partial()
    assert len(wrap.finished) == 2
    assert wrap.finished[1].type == 2


def test_partial_wrapped_partial():
    """
    Show we can parse all finished packets in the partial queue and leave incomplete ones
    """
    wrap = ds.WrappedConnection(None)
    p = ds.Packet(1)
    payload = wrap._generate_final_obj(p) * 2
    cut = payload[:-5]
    wrap._partial = cut
    wrap.parse_full_partial()
    assert len(wrap.finished) == 1
    assert wrap.finished[0] == p
    assert wrap._partial == wrap._generate_final_obj(p)[:-5]


def test_parse_sent_packet():
    # Set up basic server to respond
    port = serv.get_first_port_from(13131)
    p = ds.Packet(1, 2)
    s = serv.Server(port, partial(client_handle, ds.WrappedConnection(None)._generate_final_obj(p)))

    # Create and connect wrapped socket
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(("localhost", port))  # connecting is a blocking only operation so it must be done first
    wrap = ds.WrappedConnection(conn)

    sleep(.01)  # Socket has some delay needed
    s.shutdown()  # Now the tests can finish even when this test fails. We are assuming we make it here

    assert not wrap._partial
    wrap.load_awaited()  # Load all data from buffer
    assert wrap._partial
    wrap.parse_full_partial()
    assert not wrap._partial
    assert wrap.finished[-1] == p


def test_gen_stream():
    """
    Can the new stream format be generated
    """
    base = ascii_letters.encode("utf-8")
    prep = ds.WrappedConnection._prep_stream(base)
    assert len(prep) >= len(base) + 2  # At least two field need to be inserted


def test_parse_stream():
    """
    Can a basic stream format be parsed
    """
    base = ascii_letters.encode("utf-8")
    wrap = ds.WrappedConnection(None)
    wrap._partial = wrap._generate_final_obj(base)

    wrap.parse_full_partial()
    assert len(wrap.finished) == 1
    assert wrap.finished[0] == ascii_letters.encode("utf-8")


def test_parse_other_stream():
    """
    Test variations on stream parsing
    """
    base = ascii_uppercase.encode("utf-8")
    other = ascii_lowercase.encode("utf-8")
    wrap = ds.WrappedConnection(None)
    wrap._partial = wrap._generate_final_obj(base) + wrap._generate_final_obj(other)

    # Parse multiple streams queue up
    assert not wrap.finished
    wrap.parse_full_partial()
    assert len(wrap.finished) == 2
    assert wrap.finished[0] == ascii_uppercase.encode("utf-8")
    assert not wrap._partial

    wrap.finished = []
    wrap._partial = wrap._generate_final_obj(base) + wrap._generate_final_obj(other)[:-10]

    # Parse only finished stream parts
    wrap.parse_full_partial()
    assert len(wrap.finished) == 1
    assert wrap.finished[0] == base
    assert wrap._partial


def test_small_recv_size():
    """
    Repeat a similar test to ensure smaller recv_size's work
    """
    # Set up basic server to respond
    port = serv.get_first_port_from(13131)
    p = ascii_letters.encode()
    s = serv.Server(port, partial(client_handle, ds.WrappedConnection(None)._generate_final_obj(p)))  # Server simply sends encoded ascii

    # Create and connect wrapped socket
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(("localhost", port))  # connecting is a blocking only operation so it must be done first
    wrap = ds.WrappedConnection(conn)
    wrap.recv_size = 2

    sleep(.01)  # Socket has some delay needed
    s.shutdown()  # Now the tests can finish even when this test fails. We are assuming we make it here

    assert not wrap.finished
    wrap.parse_all()
    # print(wrap.finished)
    assert not wrap._partial
    assert wrap.finished[0] == ascii_letters.encode()





