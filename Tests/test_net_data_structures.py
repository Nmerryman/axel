import axel.services.net.data_structures as ds


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


def test_packet_gen_and_parse():
    p = ds.Packet(1, 2, 3, 4)
    gen = p.generate()
    assert len(gen) > 10
    new = ds.Packet().parse(gen)
    assert new == p
