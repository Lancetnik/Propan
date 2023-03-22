from propan.utils.classes import Singlethon


def test_singlethon():
    assert Singlethon() is Singlethon()
