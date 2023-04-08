from propan.utils.classes import Singlethon


def test_singlethon():
    assert Singlethon() is Singlethon()


def test_drop():
    s1 = Singlethon()
    s1._drop()
    assert Singlethon() is not s1
